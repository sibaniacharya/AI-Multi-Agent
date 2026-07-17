import os
from src.agents import (
    run_orchestrator,
    run_destination_agent,
    run_logistics_agent,
    run_budget_agent,
    run_review_agent,
    compile_draft_itinerary
)

def main():
    if not os.environ.get("GROQ_API_KEY") or not os.environ.get("GEMINI_API_KEY"):
        print("Please set GROQ_API_KEY and GEMINI_API_KEY environment variables to run this script.")
        print("Since keys might not be set in this isolated environment, this script serves as the structural test.")
        return

    prompt = "Plan a 3-day trip to Dubai on a $1500 budget. I love modern architecture and authentic food. Avoid crowded tourist traps if possible."
    print(f"--- USER PROMPT ---\n{prompt}\n")
    
    print("1. Orchestrator Agent extracting constraints...")
    constraints = run_orchestrator(prompt)
    print(constraints.model_dump_json(indent=2))
    
    print("\n2. Destination Agent finding places...")
    dest = run_destination_agent(constraints)
    print(dest.model_dump_json(indent=2))
    
    print("\n3. Logistics Agent planning routes...")
    logistics = run_logistics_agent(constraints, dest)
    print(logistics.model_dump_json(indent=2))
    
    print("\n4. Budget Agent calculating costs...")
    budget = run_budget_agent(constraints)
    print(budget.model_dump_json(indent=2))
    
    print("\n5. Compiling Draft Itinerary...")
    itinerary = compile_draft_itinerary(dest, logistics, budget)
    print(itinerary.model_dump_json(indent=2))
    
    print("\n6. Review Agent verifying constraints...")
    review = run_review_agent(constraints, itinerary)
    print(review.model_dump_json(indent=2))

if __name__ == "__main__":
    main()
