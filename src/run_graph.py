import os
import json
from src.graph import build_travel_graph

def main():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    if not os.environ.get("GROQ_API_KEY") or not os.environ.get("GEMINI_API_KEY"):
        print("Please set GROQ_API_KEY and GEMINI_API_KEY environment variables to run this script.")
        return
        
    app = build_travel_graph()
    
    # We use a prompt designed to potentially trigger a failure on the first pass
    # e.g., low budget but asking for luxury. The Review agent should catch it.
    initial_state = {
        "user_prompt": "Plan a 4-day trip to Dubai on a $300 budget. I want to stay in a luxury neighborhood and eat expensive food.",
        "retry_count": 0
    }
    
    print(f"--- STARTING GRAPH EXECUTION ---")
    print(f"Prompt: {initial_state['user_prompt']}\n")
    
    final_state = app.invoke(initial_state)
    
    print("\n--- FINAL ITINERARY ---")
    if final_state.get("itinerary"):
        print(final_state["itinerary"].model_dump_json(indent=2))
        
    print("\n--- FINAL REVIEW ---")
    if final_state.get("review"):
        print(final_state["review"].model_dump_json(indent=2))
        
if __name__ == "__main__":
    main()
