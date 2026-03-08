from dotenv import load_dotenv
import os
import requests
import json

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_BASE = os.getenv("API_BASE")
ENDPOINT = os.getenv("ENDPOINT")
FROM_CURRENCY = os.getenv("FROM_CURRENCY", "USD")
TO_CURRENCY = os.getenv("TO_CURRENCY", "")
AMOUNT = os.getenv("AMOUNT", "1")
FORMAT = os.getenv("FORMAT", "json")

url = f"{API_BASE}{ENDPOINT}"

params = {
    "key": API_KEY,
    "base": FROM_CURRENCY,
    "output": FORMAT
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    os.makedirs("data/raw", exist_ok=True)
    with open("data/raw/currency_data.json", "w") as f:
        json.dump(data, f, indent=4)
    print("Currency data successfully extracted and saved!")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
    print(response.text)