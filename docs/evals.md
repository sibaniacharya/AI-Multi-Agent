# Evaluation Strategy (Evals)

This document outlines the evaluation framework for the AI Travel Planner multi-agent system. Due to the non-deterministic nature of LLMs, robust evaluations are critical to ensuring the system consistently generates high-quality, valid itineraries.

## 1. Evaluation Objectives
The primary goal of this evaluation framework is to measure:
- **Constraint Adherence:** Does the final itinerary strictly respect the user's budget, duration, preferences, and avoidances?
- **Agent Accuracy:** Does each specialized agent perform its role correctly without hallucinations?
- **System Reliability:** How often does the review loop successfully catch and fix errors? What is the average number of retries?
- **Latency & Cost:** How long does the end-to-end process take, and what is the token cost per successful itinerary?

## 2. Agent-Specific Evals

### 2.1 Orchestrator Agent
- **Metric:** Extraction Accuracy
- **Test:** Compare extracted `UserConstraints` JSON against a labeled dataset of user prompts.
- **Criteria:** 100% match on Budget, Duration, and Destination. High semantic overlap on Preferences and Avoidances.

### 2.2 Destination Agent
- **Metric:** Recommendation Relevance & Grounding
- **Test:** Check if recommended attractions exist in the provided Wikivoyage/Knowledge Base.
- **Criteria:** 0% hallucination rate for locations. Strong alignment with extracted Preferences.

### 2.3 Logistics Agent
- **Metric:** Geographic Cohesion
- **Test:** Evaluate the daily clusters. Are morning, afternoon, and evening activities in the same general neighborhood?
- **Criteria:** Transit time between consecutive activities should be logically minimized.

### 2.4 Budget Agent
- **Metric:** Mathematical Accuracy
- **Test:** Re-calculate the budget outputs programmatically.
- **Criteria:** The sum of all categorized costs must equal the `total_estimated_cost` perfectly, and it must fall under the user's budget limit.

### 2.5 Review Agent
- **Metric:** QA Precision and Recall
- **Test:** Feed the Review Agent intentionally flawed itineraries (e.g., over budget, wrong city).
- **Criteria:** 
  - **Recall:** Must flag 100% of flawed itineraries (`is_valid = False`).
  - **Precision:** Must not falsely reject perfectly valid itineraries.

## 3. End-to-End Test Suite

| Test ID | Prompt | Expected Outcome | Complexity |
|---------|--------|------------------|------------|
| E2E-01 | "Plan a 3-day trip to Dubai. $1500 budget." | Valid 3-day itinerary, cost <= $1500. | Easy |
| E2E-02 | "1 day in Dubai, focus on food, avoid crowds, $500." | 1-day plan, low-traffic areas, food-heavy. | Medium |
| E2E-03 | "5 days in Dubai with a $200 budget." | System should gracefully handle the impossible constraint (e.g., flag it in review, or output max budget efficiency). | Edge Case |
| E2E-04 | "I want to see the Eiffel Tower in Dubai." | Orchestrator/Destination agent should clarify/reject the impossible request or find a replica. | Edge Case |

## 4. Automation & Tooling
Future implementation of this eval suite should utilize tools like:
- **LangSmith:** For tracing graph execution, visualizing the review loops, and monitoring token usage.
- **RAGAS / TruLens:** For programmatic evaluation of RAG retrieval (Destination agent).
- **PyTest:** For running the deterministic assertions (e.g., Budget math checks) within the CI/CD pipeline.

## 5. Evaluation Datasets (JSON)

To programmatically evaluate the agents, you can use these JSON fixtures in your test suites.

### 5.1 Orchestrator Test Cases
Use these pairs to evaluate if the Orchestrator extracts constraints accurately from natural language.

```json
[
  {
    "test_id": "ORCH-01",
    "input_prompt": "Plan a 3-day trip to Dubai. $1500 budget. I love food but want to avoid crowds.",
    "expected_output": {
      "destination": "Dubai",
      "duration_days": 3,
      "budget_usd": 1500,
      "preferences": ["food"],
      "avoidances": ["crowds"]
    }
  },
  {
    "test_id": "ORCH-02",
    "input_prompt": "I need a weekend getaway to Dubai focused entirely on modern architecture.",
    "expected_output": {
      "destination": "Dubai",
      "duration_days": 2,
      "budget_usd": 1000, 
      "preferences": ["modern architecture"],
      "avoidances": []
    }
  }
]
```

### 5.2 Review Agent Test Cases
Use these pairs to verify the Review Agent correctly flags broken constraints.

```json
[
  {
    "test_id": "REV-01",
    "description": "Fails because cost exceeds budget.",
    "mock_constraints": {
      "destination": "Dubai",
      "duration_days": 1,
      "budget_usd": 500,
      "preferences": [],
      "avoidances": []
    },
    "mock_itinerary": {
      "total_estimated_cost": 850,
      "accommodation": {"neighborhood": "Downtown Dubai", "rationale": "Central"},
      "daily_plan": [{"day": 1, "theme": "Sightseeing"}]
    },
    "expected_output": {
      "is_valid": false,
      "feedback_keywords": ["over budget", "850", "500"]
    }
  }
]
```
