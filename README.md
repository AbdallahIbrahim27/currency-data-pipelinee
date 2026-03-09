# 💱 Currency Data Pipeline

> An automated, containerized ETL pipeline that fetches, processes, and stores currency exchange rate data using **Python** and **Docker**.

[![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Pipeline Stages](#-pipeline-stages)
- [Database Schema](#-database-schema)
- [Prerequisites](#-prerequisites)
- [Environment Variables](#-environment-variables)
- [How to Run](#-how-to-run)
- [Contributing](#-contributing)

---

## 🧭 Overview

This project implements an end-to-end **ETL (Extract → Transform → Load)** pipeline for currency exchange rates. It:

1. **Extracts** live forex rates from an external currency API
2. **Transforms** and validates the raw data
3. **Loads** clean records into a PostgreSQL database

Everything runs inside **Docker containers** for fully reproducible deployment.

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCKER COMPOSE ENVIRONMENT                   │
│                                                                 │
│   ┌──────────┐    ┌──────────┐    ┌───────────┐    ┌────────┐  │
│   │  Forex   │───▶│ Extract  │───▶│ Transform │───▶│  Load  │  │
│   │   API    │    │          │    │           │    │        │  │
│   └──────────┘    └──────────┘    └───────────┘    └───┬────┘  │
│   (external)      extract.py      transform.py         │       │
│                   raw JSON        clean DataFrame       │       │
│                                                         ▼       │
│                                                  ┌──────────┐  │
│                   ┌──────────────┐               │PostgreSQL│  │
│                   │  Scheduler   │──── triggers ▶│   (db)   │  │
│                   │(APScheduler) │               └──────────┘  │
│                   └──────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🗂 Project Structure

```
currency-data-pipelinee/
│
├── docker/
│   └── docker-compose.yml      # Defines pipeline + database services
│
├── src/
│   ├── extract.py              # Stage 1: Fetch data from currency API
│   ├── transform.py            # Stage 2: Clean & normalize raw data
│   └── load.py                 # Stage 3: Write records to database
│
├── Dockerfile                  # Python image with all dependencies
├── requirements.txt            # pip dependencies
├── .gitignore                  # Excludes .env, __pycache__, etc.
└── README.md
```

---

## ⚙️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.x | All ETL logic |
| HTTP Client | `requests` | Fetching API data |
| Data Processing | `pandas` | Cleaning & transforming data |
| Database Driver | `psycopg2` / `SQLAlchemy` | PostgreSQL connection & upsert |
| Containerization | Docker + Compose | Reproducible runtime |
| Database | PostgreSQL | Persistent storage |
| Scheduling | APScheduler / cron | Automated pipeline runs |
| Config | `python-dotenv` | Environment variable management |

---

## 🔄 Pipeline Stages

### Stage 1 — Extract (`src/extract.py`)

Connects to a currency exchange rate API and retrieves live forex data via HTTP GET.

- Reads `API_KEY` and `BASE_CURRENCY` from environment variables
- Constructs the API request with query parameters
- Handles HTTP errors with retry logic
- Returns raw JSON for the next stage

```python
import requests, os
from dotenv import load_dotenv

load_dotenv()

def fetch_rates(base="USD"):
    url = f"https://api.exchangerate-api.com/v4/latest/{base}"
    headers = {"Authorization": f"Bearer {os.getenv('API_KEY')}"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()   # raises on 4xx / 5xx
    return response.json()        # { "rates": {...}, "date": "..." }
```

---

### Stage 2 — Transform (`src/transform.py`)

Converts the raw API response into a clean, typed, structured DataFrame.

- Flattens nested JSON into tabular rows
- Validates currency codes against ISO 4217
- Casts rate values to `float`, filters nulls and zeroes
- Adds ingestion timestamp and source metadata

```python
import pandas as pd
from datetime import datetime

def transform_rates(raw: dict) -> pd.DataFrame:
    records = [
        {
            "base":       raw["base"],
            "target":     currency,
            "rate":       float(rate),
            "fetched_at": datetime.utcnow(),
            "source":     "exchangerate-api"
        }
        for currency, rate in raw["rates"].items()
        if rate and rate > 0
    ]
    return pd.DataFrame(records)
```

---

### Stage 3 — Load (`src/load.py`)

Writes the cleaned DataFrame to PostgreSQL using upsert logic to prevent duplicates.

- Connects using env-based credentials
- Creates `currency_rates` table if it doesn't exist
- Executes `INSERT ... ON CONFLICT DO UPDATE`
- Logs inserted / updated / skipped row counts

```python
from sqlalchemy import create_engine
import os

def load_to_db(df):
    engine = create_engine(
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    with engine.begin() as conn:
        df.to_sql("currency_rates", conn,
                  if_exists="append", index=False, method="multi")
    print(f"✅ Loaded {len(df)} records")
```

---

## 🗄 Database Schema

```sql
CREATE TABLE IF NOT EXISTS currency_rates (
    id          SERIAL PRIMARY KEY,
    base        VARCHAR(3)     NOT NULL,            -- e.g. 'USD'
    target      VARCHAR(3)     NOT NULL,            -- e.g. 'EUR'
    rate        NUMERIC(18,8)  NOT NULL,            -- e.g. 0.92341200
    fetched_at  TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    source      VARCHAR(50),
    UNIQUE (base, target, fetched_at)
);

-- Fast time-range queries
CREATE INDEX IF NOT EXISTS idx_rates_time ON currency_rates (fetched_at DESC);

-- Fast currency-pair lookups
CREATE INDEX IF NOT EXISTS idx_rates_pair ON currency_rates (base, target);
```

---

## ✅ Prerequisites

- [Docker](https://docs.docker.com/get-docker/) v20.10+
- [Docker Compose](https://docs.docker.com/compose/install/) v2.0+
- Python 3.8+ *(only for local non-Docker execution)*
- A valid API key from a forex provider:
  - [ExchangeRate-API](https://www.exchangerate-api.com/)
  - [Fixer.io](https://fixer.io/)
  - [Open Exchange Rates](https://openexchangerates.org/)

---

## 🔐 Environment Variables

Create a `.env` file in the project root — it is already listed in `.gitignore` and must **never** be committed.

```env
# Currency API
API_KEY=your_api_key_here
BASE_CURRENCY=USD

# PostgreSQL
DB_HOST=db
DB_PORT=5432
DB_NAME=currency_db
DB_USER=postgres
DB_PASSWORD=changeme

# Optional
LOG_LEVEL=INFO
```

| Variable | Description |
|---|---|
| `API_KEY` | Authentication key for the currency API |
| `BASE_CURRENCY` | Base currency code, e.g. `USD` |
| `DB_HOST` | PostgreSQL host (`db` inside Docker) |
| `DB_PORT` | PostgreSQL port, default `5432` |
| `DB_NAME` | Target database name |
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `LOG_LEVEL` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |

---

## 🚀 How to Run

### Option 1 — Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/AbdallahIbrahim27/currency-data-pipelinee.git
cd currency-data-pipelinee

# 2. Set up environment variables
cp .env.example .env
# edit .env with your values

# 3. Build and start all services
docker-compose -f docker/docker-compose.yml up --build

# 4. Run in background
docker-compose -f docker/docker-compose.yml up -d --build

# 5. View logs
docker-compose -f docker/docker-compose.yml logs -f

# 6. Stop all services
docker-compose -f docker/docker-compose.yml down
```

### Option 2 — Local Python

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run each stage in order
python src/extract.py
python src/transform.py
python src/load.py
```

### Useful Docker Commands

| Action | Command |
|---|---|
| Start in background | `docker-compose -f docker/docker-compose.yml up -d` |
| Stop all services | `docker-compose -f docker/docker-compose.yml down` |
| Stop + remove volumes | `docker-compose -f docker/docker-compose.yml down -v` |
| Rebuild image | `docker-compose -f docker/docker-compose.yml build --no-cache` |
| Shell into container | `docker exec -it <container_name> bash` |
| Check running containers | `docker ps` |

---

## 🤝 Contributing

```bash
# 1. Fork the repository on GitHub

# 2. Create a feature branch
git checkout -b feature/your-feature-name

# 3. Commit your changes
git add .
git commit -m "feat: describe your change"

# 4. Push and open a Pull Request
git push origin feature/your-feature-name
```

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👤 Author

**Abdallah Ibrahim** — [@AbdallahIbrahim27](https://github.com/AbdallahIbrahim27)
