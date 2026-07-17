from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
import json

from src.llm_client import get_groq_llm, get_gemini_llm
from src.schemas import UserConstraints, ItineraryProposal, ReviewStatus
from src.tools import get_attractions, get_areas, get_transit_time, get_price_bands

# --- Helper Output Schemas for Agents ---

class DestinationOutput(BaseModel):
    destination_suggestions: List[Dict[str, Any]] = Field(description="List of recommended attractions/places with their details.")

class LogisticsOutput(BaseModel):
    logistics_plan: Dict[str, Any] = Field(description="Plan containing neighborhood recommendation and daily clustering.")

class BudgetOutput(BaseModel):
    budget_breakdown: Dict[str, Any] = Field(description="Estimated cost breakdown for the trip. All values must be evaluated numbers (e.g., 450), do NOT use mathematical expressions.")

# --- Agents ---

from typing import Optional

def run_orchestrator(user_prompt: str, feedback: Optional[str] = None) -> UserConstraints:
    """Extracts constraints from natural language, adjusting if feedback is provided."""
    llm = get_groq_llm().with_structured_output(UserConstraints)
    
    messages = [
        ("system", "You are the Orchestrator Agent for an AI Travel Planner. Extract travel constraints from the user prompt. Assume destination is 'Dubai' if not specified. If budget is not specified, assume 500 USD per day of the trip. IMPORTANT: Leave preferences and avoidances as empty lists unless explicitly stated by the user.")
    ]
    if feedback:
        messages.append(("system", f"PREVIOUS PLAN FAILED. Feedback from Reviewer: {feedback}. Adjust the constraints appropriately (e.g. adjust budget up, reduce days, remove conflicting preferences) to try again."))
    messages.append(("user", "{input}"))
    
    prompt = ChatPromptTemplate.from_messages(messages)
    return (prompt | llm).invoke({"input": user_prompt})

def run_destination_agent(constraints: UserConstraints) -> DestinationOutput:
    """Finds attractions matching preferences."""
    llm = get_groq_llm().with_structured_output(DestinationOutput)
    
    attractions = get_attractions()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the Destination Research Agent. Based on constraints, select the most relevant attractions from the provided knowledge base. Prioritize their preferences and avoidances."),
        ("user", "Constraints: {constraints}\nAvailable Attractions: {attractions}")
    ])
    
    return (prompt | llm).invoke({
        "constraints": constraints.model_dump_json(),
        "attractions": json.dumps(attractions)
    })

def run_logistics_agent(constraints: UserConstraints, dest_output: DestinationOutput) -> LogisticsOutput:
    """Handles routing, clustering, and accommodations."""
    llm = get_groq_llm().with_structured_output(LogisticsOutput)
    
    areas = get_areas()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the Logistics Agent. Recommend one neighborhood to stay in from the Areas list that makes sense for the chosen attractions. Also, group the attractions into logical daily clusters based on the duration of the trip to minimize transit."),
        ("user", "Constraints: {constraints}\nChosen Attractions: {attractions}\nAvailable Areas: {areas}")
    ])
    
    return (prompt | llm).invoke({
        "constraints": constraints.model_dump_json(),
        "attractions": dest_output.model_dump_json(),
        "areas": json.dumps(areas)
    })

def run_budget_agent(constraints: UserConstraints) -> BudgetOutput:
    """Estimates costs generically based on constraints (runs parallel to Logistics)."""
    llm = get_groq_llm().with_structured_output(BudgetOutput)
    
    price_bands = get_price_bands()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the Budget Agent. Calculate the generic estimated cost for the trip in USD based on the duration. Use the price_bands data to make realistic estimates. Flag if they are inherently over budget before even picking a specific hotel. IMPORTANT: Return ONLY evaluated numbers in your JSON. Do NOT output mathematical expressions like '150 * 3', evaluate them to '450' before returning."),
        ("user", "Constraints: {constraints}\nPrice Bands: {price_bands}")
    ])
    
    return (prompt | llm).invoke({
        "constraints": constraints.model_dump_json(),
        "price_bands": json.dumps(price_bands)
    })

def run_review_agent(constraints: UserConstraints, itinerary: ItineraryProposal) -> ReviewStatus:
    """QA step to ensure itinerary meets constraints using Groq to avoid Gemini 503 errors."""
    llm = get_groq_llm(temperature=0.0).with_structured_output(ReviewStatus)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the strict QA Review Agent. Check if the proposed itinerary meets all user constraints (budget, duration, preferences, avoidances). If it fails, provide clear feedback on what needs to be changed. Be strict."),
        ("user", "Constraints: {constraints}\nProposed Itinerary: {itinerary}")
    ])
    
    return (prompt | llm).invoke({
        "constraints": constraints.model_dump_json(),
        "itinerary": itinerary.model_dump_json()
    })

def compile_draft_itinerary(dest: DestinationOutput, log: LogisticsOutput, budget: BudgetOutput) -> ItineraryProposal:
    """Synthesizes agent outputs into the final ItineraryProposal schema (for testing purposes)."""
    # In a real graph, this would be an Orchestrator synthesize step.
    # We will use the Orchestrator LLM to map the raw dicts to the strict schema.
    llm = get_groq_llm().with_structured_output(ItineraryProposal)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the Orchestrator. Synthesize the sub-agent outputs into the strict ItineraryProposal schema."),
        ("user", "Destination: {dest}\nLogistics: {log}\nBudget: {budget}")
    ])
    
    return (prompt | llm).invoke({
        "dest": dest.model_dump_json(),
        "log": log.model_dump_json(),
        "budget": budget.model_dump_json()
    })
