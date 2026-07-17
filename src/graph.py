from langgraph.graph import StateGraph, START, END
from src.graph_state import TravelState
from src.agents import (
    run_orchestrator,
    run_destination_agent,
    run_logistics_agent,
    run_budget_agent,
    run_review_agent,
    compile_draft_itinerary
)

def node_orchestrator(state: TravelState):
    prompt = state.get("user_prompt", "")
    feedback = state.get("feedback")
    count = state.get("retry_count", 0)
    
    print(f"[Node: Orchestrator] Extracting constraints (Attempt {count + 1})")
    constraints = run_orchestrator(prompt, feedback)
    return {"constraints": constraints, "retry_count": count + 1}

def node_destination(state: TravelState):
    print("[Node: Destination] Finding attractions...")
    dest = run_destination_agent(state["constraints"])
    return {"dest_output": dest}

def node_logistics(state: TravelState):
    print("[Node: Logistics] Planning routes and accommodation...")
    log = run_logistics_agent(state["constraints"], state["dest_output"])
    return {"log_output": log}

def node_budget(state: TravelState):
    print("[Node: Budget] Estimating costs...")
    bud = run_budget_agent(state["constraints"])
    return {"budget_output": bud}

def node_synthesize(state: TravelState):
    print("[Node: Synthesize] Compiling draft itinerary...")
    itinerary = compile_draft_itinerary(
        state["dest_output"],
        state["log_output"],
        state["budget_output"]
    )
    return {"itinerary": itinerary}

def node_review(state: TravelState):
    print("[Node: Review] Verifying against constraints...")
    review = run_review_agent(state["constraints"], state["itinerary"])
    print(f"  -> Valid: {review.is_valid}. Feedback: {review.feedback}")
    return {"review": review, "feedback": review.feedback}

def should_continue(state: TravelState):
    review = state.get("review")
    if not review:
        return END
    
    if review.is_valid:
        return END
    
    if state.get("retry_count", 0) >= 3:
        print("[System] Max retries reached. Forcing END.")
        return END
        
    return "orchestrator"

def build_travel_graph():
    builder = StateGraph(TravelState)
    
    builder.add_node("orchestrator", node_orchestrator)
    builder.add_node("destination", node_destination)
    builder.add_node("logistics", node_logistics)
    builder.add_node("budget", node_budget)
    builder.add_node("synthesize", node_synthesize)
    builder.add_node("review", node_review)
    
    builder.add_edge(START, "orchestrator")
    builder.add_edge("orchestrator", "destination")
    
    # Fan out from destination to logistics and budget
    builder.add_edge("destination", "logistics")
    builder.add_edge("destination", "budget")
    
    # Fan in to synthesize
    builder.add_edge("logistics", "synthesize")
    builder.add_edge("budget", "synthesize")
    
    builder.add_edge("synthesize", "review")
    
    # Conditional loop
    builder.add_conditional_edges("review", should_continue, {
        "orchestrator": "orchestrator",
        END: END
    })
    
    return builder.compile()
