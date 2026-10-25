# Bookstore Analytics | AI-Powered Data Engineering Dashboard

An end-to-end Python data engineering project that transforms raw data from **five bookstores** into an interactive business intelligence dashboard with **Google Gemini-powered analytics** and natural-language chart filtering.

**[Live Dashboard](https://bookstore-analytics-ai.streamlit.app/)** · **[Source Code](https://github.com/tabayb/bookstore-analytics-ai-dashboard)**

## Overview

This project demonstrates a complete analytical workflow: reading heterogeneous source files, cleaning and joining data, resolving duplicate customer identities, calculating business metrics, and presenting insights through a web dashboard.

The application analyzes each bookstore **independently**, with a store selector and three analytical views: **Revenue**, **Customers**, and **Books**. Two AI interfaces support natural-language questions and date-based chart filtering.

## Technology Stack

| Area | Technologies |
| --- | --- |
| Data engineering | Python, pandas |
| Source formats | YAML, CSV, Parquet |
| Data processing | PyYAML, PyArrow, python-dateutil, Decimal |
| Dashboard | Streamlit |
| AI integration | Google Gemini API, Google Gen AI SDK |
| AI interactions | Function Calling, Pydantic structured responses |
| Deployment | GitHub, Streamlit Community Cloud |

## Architecture

```text
STORE1 ... STORE5
    |-- books.yaml
    |-- users.csv
    `-- orders.parquet
           |
           v
    Python ETL / Data Preparation
    |-- Parse and normalize book/author data
    |-- Normalize prices and timestamps
    |-- Reconcile customer identities
    |-- Join orders, books, and customers
    `-- Calculate revenue and sales metrics
           |
           v
    Streamlit BI Dashboard
    |-- Revenue: KPIs, top revenue days, daily trend
    |-- Customers: unique users, best buyer, aliases
    `-- Books: author sets and individual authors
           |
           +------------------------------+
           |                              |
           v                              v
    Gemini Data Assistant          Gemini Dashboard Filters
    |-- Natural-language Q&A       |-- Date extraction
    `-- Python Function Calling    `-- Revenue chart updates
```

## Key Features

### 1. Multi-store ETL

- Loads `books.yaml`, `users.csv`, and `orders.parquet` for each of five stores.
- Normalizes author combinations into order-independent sets.
- Cleans mixed price and timestamp formats before aggregation.
- Converts euro-denominated prices to USD using the **assignment-specific fixed rate of EUR 1 = USD 1.20**.
- Joins order records to books and customer identities.
- Uses an identity-reconciliation approach to link customer aliases based on matching profile fields, including name, address, phone, and email.
- Calculates sales quantities, customer spending, and daily revenue using pandas.

### 2. Business Intelligence Dashboard

**Revenue**
- Total orders and revenue metrics.
- Top five days by revenue, with dates displayed in `YYYY-MM-DD` format.
- Daily revenue trend chart.
- Natural-language date filtering of the revenue chart.

**Customers**
- Number of reconciled unique users and unique buyers.
- Best buyer, total spending, and associated user IDs shown as an array.
- Top five buyers by total spending.

**Books**
- Number of unique sets of authors.
- Top five author sets by quantity sold.
- Most popular individual author(s), including ties in the displayed ranking.
- Top five individual authors by quantity sold.

### 3. AI Data Assistant

The Gemini-powered chat can answer questions about the selected store through **predefined Python functions** that compute results from pandas DataFrames. This avoids executing arbitrary AI-generated code.

Example prompts:

```text
Who is the best buyer?
What are the top five best-selling books?
What is the most expensive book sold?
Which authors sold the most books?
How much revenue was generated between 2026-01-01 and 2026-03-31?
```

The chat has a scrollable message history, a clear-chat action, and store-specific context. Questions outside the available data or functions may not be answerable.

### 4. AI Dashboard Filters

A separate Gemini-powered chat interprets natural-language date requests, validates structured start/end dates, and updates the **Daily Revenue Trend** chart.

Example commands:

```text
Show revenue for March 2026
Show revenue from January 10 to January 25, 2026
```

**Scope:** The AI date filter currently applies to the daily revenue chart only; dashboard-wide KPIs and top-five tables continue to represent their original reporting scope.

## Repository Structure

```text
bookstore-analytics-ai-dashboard/
|-- STORE1/
|   |-- books.yaml
|   |-- orders.parquet
|   `-- users.csv
|-- STORE2/                 # Same three source files
|-- STORE3/
|-- STORE4/
|-- STORE5/
|-- app.py                  # Streamlit interface and AI chart filtering
|-- ai_tools.py             # Gemini Function Calling analytics
|-- explore_books.py        # Book and author transformations
|-- explore_users.py        # Customer reconciliation and buyer metrics
|-- explore_data.py         # Revenue and date transformations
|-- test_date.py            # Date parsing development checks
|-- test_prices.py          # Price parsing development checks
|-- requirements.txt
|-- .gitignore
`-- README.md
```

## Run Locally

**Prerequisites:** Python 3.11+ and a Gemini API key for the AI features.

```bash
git clone https://github.com/tabayb/bookstore-analytics-ai-dashboard.git
cd bookstore-analytics-ai-dashboard

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1` instead.

Create a local Streamlit secrets file at `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

**Never commit your actual API key.** The `.streamlit/secrets.toml` path is excluded by `.gitignore`.

Start the application:

```bash
streamlit run app.py
```

Open **http://localhost:8501** and choose a bookstore from the selector.

## Cloud Deployment

The live application runs on **Streamlit Community Cloud** using the repository's `main` branch and `app.py` entry point.

To deploy your own copy:

1. Fork the repository and connect your GitHub account to Streamlit Community Cloud.
2. Create a new app using `app.py` on `main`.
3. Add `GEMINI_API_KEY = "..."` in the app's **Secrets** settings (not in GitHub).
4. Deploy and test the three dashboard views and both AI chats.

Gemini API usage is subject to the quota and terms of the account supplying the key.

## Data Quality and Limitations

- **Store isolation:** Metrics and customer identity reconciliation are calculated independently for each bookstore.
- **Customer matching:** Identity resolution is heuristic; records that look similar are not guaranteed to represent the same person.
- **Currency conversion:** The EUR-to-USD rate is fixed for this assignment, not a live market exchange rate.
- **Timestamp parsing:** Multiple source date formats are normalized, but ambiguous dates require careful validation.
- **AI grounding:** Gemini can retrieve additional facts only through the analytical functions exposed to it; it does not have unrestricted access to run generated Python or SQL.
- **Public demo:** The hosted AI features depend on external API availability and free-tier limits.
- **Source data:** The included bookstore files are educational project data. Anyone reusing or redistributing them should confirm the applicable permissions and privacy requirements.

## Future Improvements

- Make AI date filters apply consistently to KPI cards, tables, and charts.
- Add automated unit tests, data quality assertions, and CI checks.
- Expand safe AI analytical functions and conversational context handling.
- Add configurable exchange rates and more robust identity-resolution evaluation.
- Introduce scheduled ingestion and persistent analytical storage.

## Project Status

**Deployed and accessible online.** The five-store ETL pipeline, three-view Streamlit dashboard, Gemini AI Data Assistant, and natural-language revenue chart filters have been implemented and tested.

**[Try the Live Dashboard](https://bookstore-analytics-ai.streamlit.app/)**