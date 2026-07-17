from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class UserConstraints(BaseModel):
    destination: str = Field(description="The destination for the trip.")
    duration_days: int = Field(description="Duration of the trip in days.")
    budget_usd: float = Field(description="Total budget for the trip in USD.")
    preferences: List[str] = Field(default_factory=list, description="User's preferences, if explicitly stated.")
    avoidances: List[str] = Field(default_factory=list, description="What the user wants to avoid, if explicitly stated.")

class AgentOutputs(BaseModel):
    destination_suggestions: List[Dict[str, Any]] = Field(default_factory=list, description="Points of interest from Destination Agent.")
    logistics_plan: Dict[str, Any] = Field(default_factory=dict, description="Routing and accommodations from Logistics Agent.")
    budget_breakdown: Dict[str, Any] = Field(default_factory=dict, description="Cost breakdown from Budget Agent.")

class DailyActivity(BaseModel):
    day: int = Field(description="Day number of the trip.")
    theme: str = Field(description="Theme for the day.")
    morning_activity: str = Field(description="Activity planned for the morning.")
    afternoon_activity: str = Field(description="Activity planned for the afternoon.")
    evening_activity: str = Field(description="Activity planned for the evening.")
    transit_notes: str = Field(description="Transit information for the day.")

class Accommodation(BaseModel):
    neighborhood: str = Field(description="Neighborhood suggested for stay.")
    rationale: str = Field(description="Reason for suggesting this neighborhood.")

class ItineraryProposal(BaseModel):
    total_estimated_cost: float = Field(description="Total estimated cost in USD.")
    accommodation: Accommodation
    daily_plan: List[DailyActivity]

class ReviewStatus(BaseModel):
    is_valid: bool = Field(description="True if the itinerary passes constraints, False otherwise.")
    feedback: str = Field(description="Feedback on why it failed or confirmation of success.")

class TravelGraphState(BaseModel):
    constraints: Optional[UserConstraints] = None
    agent_outputs: AgentOutputs = Field(default_factory=AgentOutputs)
    itinerary: Optional[ItineraryProposal] = None
    review_status: Optional[ReviewStatus] = None
    retry_count: int = 0
