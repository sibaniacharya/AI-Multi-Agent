from typing import TypedDict, Optional, Dict, Any
from src.schemas import UserConstraints, ItineraryProposal, ReviewStatus
from src.agents import DestinationOutput, LogisticsOutput, BudgetOutput

class TravelState(TypedDict, total=False):
    # Input / Meta
    user_prompt: str
    feedback: Optional[str]
    retry_count: int
    
    # Extracted Constraints
    constraints: Optional[UserConstraints]
    
    # Parallel Agent Outputs
    dest_output: Optional[DestinationOutput]
    log_output: Optional[LogisticsOutput]
    budget_output: Optional[BudgetOutput]
    
    # Synthesized and Reviewed
    itinerary: Optional[ItineraryProposal]
    review: Optional[ReviewStatus]
