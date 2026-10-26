# Customer Analytics Platform

An automated, scheduled analytics pipeline: it ingests multi-format customer data into a local warehouse, segments customers, scores churn risk, forecasts revenue, and publishes a dashboard and PDF report every morning with no manual steps.

**Live dashboard:** [customer-analytics-sj.streamlit.app](https://customer-analytics-sj.streamlit.app/)

> **About the data:** this project runs on a **synthetic dataset** generated with Python's Faker library (2,000 customers, 10,000 orders, 40 products, 50,000 events). It's a simulated scenario built to demonstrate pipeline automation and orchestration, and the data is regenerated on each run, so exact numbers change between runs.

## The scenario

Imagine a mid-size online retailer that can't easily answer three questions: which customers are most valuable, which are drifting away, and what revenue to expect next month. This project automates those answers on a daily schedule.

## Architecture

```
Raw data (CSV / JSON / Parquet)
        ↓
DuckDB (local warehouse)
        ↓
Models (scikit-learn + Prophet)
    ├── Customer segmentation (RFM quartile scoring)
    ├── Churn risk scoring (Random Forest)
    └── 30-day revenue forecast (Prophet)
        ↓
Streamlit dashboard + PDF report
        ↓
Orchestrated with Prefect, scheduled daily at 6:00 AM
```

## What it does

- **Multi-format ingestion:** CSV, JSON and Parquet loaded into DuckDB (`pipeline/load_data.py`)
- **Segmentation:** RFM quartile scores group customers into Champions, Loyal, At Risk and Lost
- **Churn risk:** a Random Forest assigns each customer a Low / Medium / High risk band
- **Forecasting:** 30-day revenue forecast with confidence intervals using Prophet
- **Reporting:** a Streamlit dashboard plus an auto-generated PDF report
- **Orchestration:** a Prefect flow runs every step in order, on a daily cron schedule

## Sample output (one run)

- 2,000 customers segmented into four RFM groups
- 1,275 customers in the High churn-risk band
- About $182,580 projected revenue for the next 30 days, with confidence intervals
- PDF report generated automatically

## Known limitation: churn model

Churn is currently labelled as "recency over 90 days," and recency is also a model input, so the Random Forest is effectively relearning that rule. That's also why so many customers (about 64%) land in the high-risk band: in this synthetic data, most customers simply haven't ordered recently.

**Next step:** build features from activity before a cutoff date, and label churn by whether the customer buys in the following 90 days. Then evaluate with precision and recall on the churn class, not just accuracy.

## Tech stack

| Layer | Tool |
|---|---|
| Data generation | Python, Faker |
| Warehouse | DuckDB |
| ML | scikit-learn, Prophet |
| Dashboard | Streamlit, Plotly |
| Reports | ReportLab |
| Orchestration | Prefect |
| Version control | Git |

## Project structure

```
Customer-analytics/
├── data/generate_data.py    # Synthetic data generator
├── pipeline/
│   ├── load_data.py         # Load CSV / JSON / Parquet into DuckDB
│   └── orchestrate.py       # Prefect flow (all steps, in order)
├── ml/
│   ├── segmentation.py      # RFM segmentation
│   ├── churn.py             # Churn risk model
│   └── forecast.py          # Prophet revenue forecast
├── app/dashboard.py         # Streamlit dashboard
├── reports/report_generator.py  # PDF report
├── prefect.yaml             # Daily 6 AM schedule
└── requirements.txt
```

## Run it locally

```bash
git clone https://github.com/shaarvarij/Customer-analytics.git
cd Customer-analytics
pip install -r requirements.txt
python3 pipeline/orchestrate.py   # runs the full pipeline once
streamlit run app/dashboard.py
```

## Author

**Sharvari Joshi** · [LinkedIn](https://www.linkedin.com/in/sharvarijoshi) · [GitHub](https://github.com/shaarvarij)
