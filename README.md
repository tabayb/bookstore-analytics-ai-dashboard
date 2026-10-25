# Bookstore Analytics — AI-Powered Data Engineering Dashboard

An end-to-end Data Engineering project that transforms raw bookstore data into interactive business intelligence dashboards and enables natural-language data analysis using Google Gemini AI.

## Project Overview

The platform processes data from **five independent bookstores**, cleans and transforms source files, reconciles customer identities, calculates business metrics, and presents analytical insights through Streamlit.

The project combines traditional ETL processing with AI-powered analytics and dashboard filtering.

## Tech Stack

- **Python** — Data processing and ETL
- **pandas** — Data transformation and aggregation
- **Parquet / CSV / YAML** — Source data formats
- **Streamlit** — Interactive BI dashboard
- **Google Gemini API** — Natural-language analytics
- **Function Calling** — AI access to predefined analytical functions
- **Pydantic** — Structured AI responses
- **Git / GitHub** — Version control

## Architecture

```text
Raw Data (5 Stores)
       |
       +-- books.yaml
       +-- users.csv
       +-- orders.parquet
       |
       v
Python ETL Pipeline
       |
       +-- Data Cleaning
       +-- Customer Identity Resolution
       +-- Price and Timestamp Normalization
       +-- Revenue and Author Aggregations
       |
       v
Streamlit BI Dashboard
       |
       +-- Revenue Analytics
       +-- Customer Analytics
       +-- Book & Author Analytics
       |
       v
Gemini AI Integration
       |
       +-- Natural-Language Questions
       +-- Function Calling
       +-- AI-Controlled Revenue Date Filters
```

## Key Features

### 1. ETL and Data Processing

- Ingest YAML, CSV, and Parquet datasets.
- Normalize inconsistent prices and timestamps.
- Convert EUR prices to USD using the assignment's fixed exchange rate.
- Reconcile duplicate customer identities using matching attributes.
- Combine orders with book and customer records.
- Calculate daily revenue and sales rankings.

### 2. Business Intelligence Dashboard

Three analytical views:

**Revenue**
- Total revenue and order metrics
- Top five revenue days
- Daily revenue trends
- AI-controlled date filtering for the revenue chart

**Customers**
- Reconciled unique customer counts
- Unique buyers
- Top spending customers
- Associated customer identifiers

**Books**
- Best-selling author combinations
- Individual author rankings
- Quantity-based sales analysis

### 3. Gemini AI Data Assistant

Integrates Google Gemini with Python Function Calling to answer analytical questions using the processed datasets.

Example questions:

- Who is the highest-spending customer?
- What is the most expensive book sold?
- What are the top five best-selling books?
- Which authors sold the most books?
- How much revenue was generated within a specified date range?

AI functions perform deterministic calculations using pandas rather than executing arbitrary model-generated Python code.

### 4. AI Dashboard Filtering

Users can control the revenue chart through natural-language commands.

Example:

> Show revenue for March 2026.

Gemini extracts a structured date range, and Streamlit updates the revenue visualization.

## Project Structure

```text
bookstore-analytics-ai-dashboard/
├── app.py
├── ai_tools.py
├── explore_books.py
├── explore_users.py
├── explore_data.py
├── test_date.py
├── test_prices.py
├── requirements.txt
├── .gitignore
└── README.md
```

The application also requires bookstore datasets in the expected `STORE1`–`STORE5` directory structure. Public distribution of those datasets is subject to privacy and sharing permissions.

## Running Locally

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd bookstore-analytics-ai-dashboard
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Place authorized input datasets in the expected store directories, then launch:

```bash
streamlit run app.py
```

Open `http://localhost:8501`.

## Data Quality Considerations

The pipeline includes timestamp normalization, price validation, relational joins, and customer identity reconciliation.

Customer reconciliation is heuristic and may require additional validation for production use.

## Future Improvements

- Expanded AI-driven dashboard interactions
- Automated data quality checks
- Additional analytical visualizations
- CI/CD and cloud deployment
- More comprehensive automated testing

## Project Status

**Functional locally.** ETL, Streamlit dashboards, Gemini analytical questions, and AI revenue-date filtering have been implemented and tested.

Public deployment and sanitized demo data preparation are planned.