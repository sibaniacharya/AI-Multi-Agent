import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

WIKIVOYAGE_URL = "https://en.wikivoyage.org/wiki/Dubai"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "dubai")

def create_skeleton_files():
    """Create the skeleton JSON files for structured data."""
    # areas.json
    with open(os.path.join(OUTPUT_DIR, "areas.json"), "w") as f:
        json.dump({"areas": [{"name": "Downtown Dubai", "description": ""}]}, f, indent=2)
    
    # attractions.json
    with open(os.path.join(OUTPUT_DIR, "attractions.json"), "w") as f:
        json.dump({"attractions": [{"name": "Burj Khalifa", "area": "Downtown Dubai", "category": "See"}]}, f, indent=2)
        
    # price_bands.json
    with open(os.path.join(OUTPUT_DIR, "price_bands.json"), "w") as f:
        json.dump({"currency": "AED", "bands": {"budget": {"food": 50, "stay": 200}}}, f, indent=2)
        
    # transit_matrix.json
    with open(os.path.join(OUTPUT_DIR, "transit_matrix.json"), "w") as f:
        json.dump({"matrix": [{"from": "Downtown Dubai", "to": "Dubai Marina", "time_mins": 25, "mode": "Metro"}]}, f, indent=2)
        
    # manifest.json
    manifest = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source_url": WIKIVOYAGE_URL,
        "files": ["areas.json", "attractions.json", "price_bands.json", "transit_matrix.json", "wikivoyage_api.json", "wikivoyage_raw.md"]
    }
    with open(os.path.join(OUTPUT_DIR, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

def scrape_wikivoyage():
    print(f"Fetching data from {WIKIVOYAGE_URL}...")
    headers = {
        'User-Agent': 'AI-Travel-Planner-Bot/1.0 (https://github.com/example/repo; bot@example.com)'
    }
    response = requests.get(WIKIVOYAGE_URL, headers=headers)
    response.raise_for_status()
    
    # Ensure data/dubai directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Save raw markdown (approximate, saving raw HTML text)
    soup = BeautifulSoup(response.text, "html.parser")
    with open(os.path.join(OUTPUT_DIR, "wikivoyage_raw.md"), "w", encoding="utf-8") as f:
        f.write(f"# Dubai Wikivoyage Raw\n\n{soup.get_text(separator=' ', strip=True)}")
    
    target_sections = ["Get_around", "See", "Do", "Buy", "Eat", "Drink", "Sleep"]
    knowledge_base = {}
    
    for section_id in target_sections:
        heading = soup.find(id=section_id)
        if not heading:
            print(f"Warning: Could not find section '{section_id}'")
            continue
        
        h2 = heading.parent
        content = []
        
        current_node = h2.find_next_sibling()
        while current_node and current_node.name != "h2":
            if current_node.name in ["p", "ul", "h3", "h4", "div"]:
                text = current_node.get_text(strip=True, separator=" ")
                if text:
                    content.append(text)
            current_node = current_node.find_next_sibling()
            
        knowledge_base[section_id] = "\n\n".join(content)
        print(f"Extracted {len(content)} blocks for section '{section_id}'.")
        
    api_file = os.path.join(OUTPUT_DIR, "wikivoyage_api.json")
    with open(api_file, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
        
    create_skeleton_files()
    print(f"Successfully generated data structure in {OUTPUT_DIR}")

if __name__ == "__main__":
    scrape_wikivoyage()
