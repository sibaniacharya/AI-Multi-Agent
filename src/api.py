from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import asyncio
import os
from dotenv import load_dotenv
from groq import Groq

# Ensure local .env is loaded
load_dotenv()

# We import the graph after loading dotenv so any module-level env checks pass (though our agents fetch dynamically, it's safer)
from src.graph import build_travel_graph

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Travel Planner API",
    description="Multi-agent graph workflow for generating travel itineraries."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development/production simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

graph = build_travel_graph()

class PlanTripRequest(BaseModel):
    prompt: str

@app.post("/plan-trip")
async def plan_trip(request: PlanTripRequest):
    if not os.environ.get("GROQ_API_KEY") or not os.environ.get("GEMINI_API_KEY"):
        raise HTTPException(status_code=500, detail="Missing API keys in environment variables.")
    
    initial_state = {
        "user_prompt": request.prompt,
        "retry_count": 0
    }
    
    try:
        final_state = graph.invoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {str(e)}")
        
    itinerary = final_state.get("itinerary")
    if not itinerary:
        raise HTTPException(status_code=500, detail="Failed to generate a complete itinerary after maximum retries.")
        
    review = final_state.get("review")
    
    return {
        "status": "success",
        "itinerary": itinerary.model_dump(),
        "qa_review": review.model_dump() if review else None
    }

@app.get("/stream-plan-trip")
async def stream_plan_trip(prompt: str):
    if not os.environ.get("GROQ_API_KEY") or not os.environ.get("GEMINI_API_KEY"):
        raise HTTPException(status_code=500, detail="Missing API keys in environment variables.")

    initial_state = {
        "user_prompt": prompt,
        "retry_count": 0
    }

    async def event_generator():
        queue = asyncio.Queue()
        
        async def run_graph():
            try:
                async for output in graph.astream(initial_state):
                    await queue.put({"type": "data", "payload": output})
                await queue.put({"type": "done"})
            except Exception as e:
                await queue.put({"type": "error", "payload": str(e)})
                
        task = asyncio.create_task(run_graph())
        
        get_task = None
        while True:
            if get_task is None:
                get_task = asyncio.create_task(queue.get())
                
            done, pending = await asyncio.wait([get_task], timeout=5.0)
            
            if get_task in done:
                msg = get_task.result()
                get_task = None
                
                if msg["type"] == "done":
                    yield f"data: {json.dumps({'node': 'DONE', 'status': 'completed'})}\n\n"
                    break
                elif msg["type"] == "error":
                    yield f"data: {json.dumps({'error': msg['payload']})}\n\n"
                    break
                else:
                    output = msg["payload"]
                    for key, value in output.items():
                        event_data = {
                            "node": key,
                            "status": "completed",
                            "retry_count": value.get("retry_count", 0)
                        }
                        
                        if "itinerary" in value and value["itinerary"]:
                            itinerary_dump = value["itinerary"].model_dump() if hasattr(value["itinerary"], "model_dump") else value["itinerary"]
                            event_data["itinerary"] = itinerary_dump
                        
                        if "review" in value and value["review"]:
                            review_dump = value["review"].model_dump() if hasattr(value["review"], "model_dump") else value["review"]
                            event_data["qa_review"] = review_dump

                        yield f"data: {json.dumps(event_data)}\n\n"
                        
            else:
                # Timeout occurred, send keep-alive
                yield ": keepalive\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise HTTPException(status_code=500, detail="Missing GROQ_API_KEY in environment variables.")
    
    try:
        client = Groq(api_key=groq_api_key)
        # Read the file content into memory
        file_content = await audio.read()
        
        # Groq client expects a tuple of (filename, file_content)
        transcription = client.audio.transcriptions.create(
            file=(audio.filename, file_content),
            model="whisper-large-v3",
        )
        return {"text": transcription.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
