import pytest
from fastapi.testclient import TestClient
from src.api import app
from src.graph import build_travel_graph

client = TestClient(app)

def test_plan_trip_api_endpoint():
    """
    Test the /plan-trip API endpoint directly.
    """
    response = client.post(
        "/plan-trip",
        json={"prompt": "Plan a 1-day trip to Dubai focusing on Burj Khalifa."}
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["status"] == "success"
    assert "itinerary" in data
    assert "qa_review" in data

def test_plan_trip_review_loop():
    """
    End-to-End Test specifically targeting the Review loop.
    Intentionally request a $500 budget for 5 luxury days in Dubai to ensure 
    the system rejects and adjusts it. We test the graph directly to observe state.
    """
    prompt = "I want a 5-day luxury trip to Dubai but my budget is only $500. It must be luxury."
    
    graph = build_travel_graph()
    initial_state = {
        "user_prompt": prompt,
        "retry_count": 0
    }
    
    final_state = graph.invoke(initial_state)
    
    # Verify that retries happened (meaning the review loop failed at least once)
    # The review agent should flag $500 as too low for 5 days of luxury in Dubai.
    assert final_state.get("retry_count", 0) > 0, "Expected the review loop to trigger at least one retry due to tight budget vs luxury constraints."
    
    # Verify we eventually got an itinerary
    assert "itinerary" in final_state
    
    review = final_state.get("review")
    if review:
        print("Final Review Valid:", review.is_valid)
        print("Final Review Feedback:", review.feedback)
