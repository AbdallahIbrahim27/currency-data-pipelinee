# 💱 Currency Data Pipeline

An automated, containerized ETL pipeline that fetches, processes, and stores currency exchange rate data using Python and Docker.

---

## 📌 Overview

This project implements an end-to-end data pipeline for currency exchange rates. It extracts live or historical forex data from an external API, applies transformations and validation, and loads the results into a target data store — all orchestrated inside Docker containers for easy, reproducible deployment.

```
[Currency API] ──► [Extract] ──► [Transform] ──► [Load / Store]
                                                        │
                                              [PostgreSQL / CSV / DB]
```

---

## 🗂️ Project Structure

```
currency-data-pipelinee/
│
├── docker/                  # Docker Compose and service configurations
│   └── docker-compose.yml
│
├── scripts/                 # Python ETL scripts
│   ├── extract.py           # Fetches currency data from the API
│   ├── transform.py         # Cleans and normalizes the raw data
│   └── load.py              # Loads processed data into the target store
│
├── Dockerfile               # Container image definition for the pipeline
├── requirements.txt         # Python dependencies
├── .gitignore
└── README.md
```

---

## ⚙️ Tech Stack

| Component     | Technology              |
|---------------|-------------------------|
| Language       | Python 3.x              |
| Containerization | Docker & Docker Compose |
| Data Source   | Currency Exchange API   |
| Data Processing | Pandas / Requests       |
| Storage       | PostgreSQL / CSV        |

---

## 🔧 Prerequisites

Make sure you have the following installed before running the project:

- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)
- Python 3.8+ *(only if running locally without Docker)*
- A valid API key from your currency data provider (e.g., [ExchangeRate-API](https://www.exchangerate-api.com/), [Fixer.io](https://fixer.io/), or [Open Exchange Rates](https://openexchangerates.org/))

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/AbdallahIbrahim27/currency-data-pipelinee.git
cd currency-data-pipelinee
```

### 2. Configure Environment Variables

Create a `.env` file in the project root and fill in your credentials:

```env
# Currency API
API_KEY=your_api_key_here
BASE_CURRENCY=USD

# Database (if applicable)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=currency_db
DB_USER=postgres
DB_PASSWORD=your_password
```

> ⚠️ **Never commit your `.env` file.** It is already listed in `.gitignore`.

---

## 🐳 Running with Docker (Recommended)

### Build and Start All Services

```bash
docker-compose -f docker/docker-compose.yml up --build
```

This will:
1. Build the pipeline image from the `Dockerfile`
2. Start all required services (database, pipeline runner)
3. Execute the ETL pipeline automatically

### Run in Detached Mode

```bash
docker-compose -f docker/docker-compose.yml up -d --build
```

### Stop All Services

```bash
docker-compose -f docker/docker-compose.yml down
```

### View Logs

```bash
docker-compose -f docker/docker-compose.yml logs -f
```

---

## 🐍 Running Locally (Without Docker)

### 1. Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Pipeline

Execute the scripts in order:

```bash
# Step 1: Extract data from the currency API
python scripts/extract.py

# Step 2: Transform and clean the data
python scripts/transform.py

# Step 3: Load data into the target store
python scripts/load.py
```

Or run them all together if a main entry point is provided:

```bash
python scripts/main.py
```

---

## 📊 Pipeline Stages

### 1. Extract
- Connects to the currency exchange rate API
- Fetches rates for configured currency pairs
- Saves raw response data for processing

### 2. Transform
- Parses and validates the raw API response
- Normalizes currency codes and rate values
- Handles missing values and data type conversion
- Adds metadata (timestamps, source info)

### 3. Load
- Inserts cleaned records into the target database or CSV file
- Handles upserts to avoid duplicate entries
- Logs pipeline run statistics

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👤 Author

**Abdallah Ibrahim**  
GitHub: [@AbdallahIbrahim27](https://github.com/AbdallahIbrahim27)
