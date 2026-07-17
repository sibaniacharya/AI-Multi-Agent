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

app = FastAPI(
    title="AI Travel Planner API",
    description="Multi-agent graph workflow for generating travel itineraries."
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
        try:
            # Use .astream() which is asynchronous and won't block the event loop
            async for output in graph.astream(initial_state):
                for key, value in output.items():
                    # key is the node name (e.g., 'orchestrator', 'destination', etc.)
                    # Yield a JSON event
                    event_data = {
                        "node": key,
                        "status": "completed",
                        "retry_count": value.get("retry_count", 0)
                    }
                    
                    # If this is the synthesize node, it might contain the final itinerary
                    if "itinerary" in value and value["itinerary"]:
                        # Convert Pydantic object if it's there
                        itinerary_dump = value["itinerary"].model_dump() if hasattr(value["itinerary"], "model_dump") else value["itinerary"]
                        event_data["itinerary"] = itinerary_dump
                    
                    if "review" in value and value["review"]:
                        review_dump = value["review"].model_dump() if hasattr(value["review"], "model_dump") else value["review"]
                        event_data["qa_review"] = review_dump

                    yield f"data: {json.dumps(event_data)}\n\n"
                    # Small sleep to ensure chunks are flushed properly
                    await asyncio.sleep(0.1)
            
            # Send an explicit completion event
            yield f"data: {json.dumps({'node': 'DONE', 'status': 'completed'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

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
    uvicorn.run(app, host="0.0.0.0", port=8000)
