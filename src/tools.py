import os
import json
from typing import List, Dict, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "dubai")

def _load_json(filename: str) -> Dict[str, Any]:
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_attractions(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns a list of attractions, optionally filtered by category (e.g. 'See', 'Buy', 'Eat', 'Do')."""
    data = _load_json("attractions.json")
    attractions = data.get("attractions", [])
    if category:
        attractions = [a for a in attractions if a.get("category", "").lower() == category.lower()]
    return attractions

def get_areas() -> List[Dict[str, Any]]:
    """Returns a list of neighborhoods/areas in Dubai."""
    return _load_json("areas.json").get("areas", [])

def get_transit_time(from_area: str, to_area: str) -> Optional[Dict[str, Any]]:
    """Returns the transit time and mode between two areas."""
    data = _load_json("transit_matrix.json")
    matrix = data.get("matrix", [])
    for entry in matrix:
        if (entry.get("from") == from_area and entry.get("to") == to_area) or \
           (entry.get("from") == to_area and entry.get("to") == from_area):
            return entry
    return None

def get_price_bands() -> Dict[str, Any]:
    """Returns the daily price estimates for budget, mid_range, and luxury."""
    return _load_json("price_bands.json")

def get_wikivoyage_text(section: str) -> str:
    """Returns the raw text from Wikivoyage for a specific section (e.g., 'Eat', 'Sleep')."""
    data = _load_json("wikivoyage_api.json")
    return data.get(section, "")
