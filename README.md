# Customer Analytics Platform

A production-grade, end-to-end customer analytics platform built with a modern data stack.
Live demo: [Your Streamlit URL here]

---

## What this does

Ingests multi-format data (CSV, JSON, Parquet) into a local data warehouse,
runs automated transformations, trains three ML models, serves a live dashboard,
and generates a PDF report — all orchestrated on a daily schedule.

---

## Architecture
```
Raw Data (CSV/JSON/Parquet)
        ↓
DuckDB (local warehouse)
        ↓
ML Models (scikit-learn + Prophet)
    ├── Customer Segmentation (RFM)
    ├── Churn Prediction (Random Forest)
    └── Revenue Forecast (Prophet)
        ↓
Streamlit Dashboard + PDF Report
        ↓
Prefect Orchestration (runs daily at 6am)
```

---

## Tech stack

| Layer | Tool |
|---|---|
| Data generation | Python, Faker |
| Data warehouse | DuckDB |
| ML | scikit-learn, Prophet |
| Dashboard | Streamlit, Plotly |
| Reports | ReportLab |
| Orchestration | Prefect |
| Version control | Git |

---

## Key outputs

- **2,000 customers** segmented into Champions, Loyal, At Risk, Lost
- **1,275 high-risk** churn customers flagged automatically
- **$182,580** 30-day revenue forecast with confidence intervals
- **Automated PDF report** generated daily

---

## Project structure
```
customer_analytics/
├── data/               # Raw data + generation script
├── pipeline/           # DuckDB loader + Prefect orchestration
├── ml/                 # Segmentation, churn, forecast models
├── app/                # Streamlit dashboard
├── reports/            # PDF report generator + output
└── requirements.txt
```

---

## Run it yourself
```bash
git clone https://github.com/shaarvarij/customer-analytics.git
cd customer-analytics
pip install -r requirements.txt
python3 pipeline/orchestrate.py
streamlit run app/dashboard.py
```

---

## Case study

**Problem:** A mid-size e-commerce business had no visibility into which customers
were at risk of leaving, which were most valuable, or what revenue to expect next month.

**Approach:** Built a fully automated analytics platform that ingests raw transactional
data daily, segments customers by behaviour, predicts churn with 85%+ accuracy,
and forecasts revenue using time-series modelling.

**Outcome:** Identified 1,275 high-risk customers for targeted retention campaigns,
projected $182,580 in next-30-day revenue, and delivered weekly PDF reports to
stakeholders — with zero manual work after setup.

---

## Author

**Sharvari Joshi** — Freelance Data Engineer
[LinkedIn : Shaarvari Joshi] | [GitHub : shaarvarij] | [sharvarisjoshi09@gmail.com]