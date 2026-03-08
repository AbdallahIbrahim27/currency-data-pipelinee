from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Load transformed data
df = pd.read_csv("data/transformed/currency_data.csv")

# Connect to PostgreSQL
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    print("Connected to PostgreSQL successfully!")
except Exception as e:
    print("Error connecting to PostgreSQL:", e)
    exit(1)

# Create table if not exists
create_table_query = """
CREATE TABLE IF NOT EXISTS currency_rates (
    id SERIAL PRIMARY KEY,
    base VARCHAR(3),
    target VARCHAR(10),
    rate FLOAT,
    updated TIMESTAMP
)
"""
cursor.execute(create_table_query)
conn.commit()

# Insert data
insert_query = """
INSERT INTO currency_rates (base, target, rate, updated)
VALUES (%s, %s, %s, %s)
ON CONFLICT DO NOTHING
"""

for _, row in df.iterrows():
    cursor.execute(insert_query, (row['base'], row['target'], row['rate'], row['updated']))

conn.commit()
cursor.close()
conn.close()
print("Data loaded into PostgreSQL successfully!")