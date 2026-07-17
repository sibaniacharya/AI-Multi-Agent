import requests
import json
import time

url = "http://127.0.0.1:8000/plan-trip"
headers = {"Content-Type": "application/json"}
data = {
    "prompt": "Plan a 2-day trip to Dubai on a $200 budget. Keep it cheap."
}

print(f"Sending request to {url}...")
try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
except requests.exceptions.ConnectionError:
    print("Connection failed. Is the server running?")
