import os
import json
import pandas as pd
from datetime import datetime

# Load raw data
with open("data/raw/currency_data.json") as f:
    raw_data = json.load(f)

# Transform data
records = []
timestamp = datetime.utcnow()

for target, rate in raw_data.get("rates", {}).items():
    records.append({
        "base": raw_data.get("base", "USD"),
        "target": target,
        "rate": rate,
        "updated": timestamp
    })

df = pd.DataFrame(records)
os.makedirs("data/transformed", exist_ok=True)
df.to_csv("data/transformed/currency_data.csv", index=False)

print("Transformation done! CSV saved to data/transformed/currency_data.csv")
print(df.head())
