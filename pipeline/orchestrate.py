from prefect import flow, task
from prefect import flow, task
import subprocess
import sys
import subprocess
import sys

@task(name="Generate data", log_prints=True)
def generate_data():
    subprocess.run([sys.executable, "data/generate_data.py"], check=True)

@task(name="Load to DuckDB", log_prints=True)
def load_to_duckdb():
    subprocess.run([sys.executable, "pipeline/load_data.py"], check=True)

@task(name="Customer segmentation", log_prints=True)
def run_segmentation():
    subprocess.run([sys.executable, "ml/segmentation.py"], check=True)

@task(name="Churn prediction", log_prints=True)
def run_churn():
    subprocess.run([sys.executable, "ml/churn.py"], check=True)

@task(name="Revenue forecast", log_prints=True)
def run_forecast():
    subprocess.run([sys.executable, "ml/forecast.py"], check=True)

@task(name="Generate PDF report", log_prints=True)
def generate_report():
    subprocess.run([sys.executable, "reports/report_generator.py"], check=True)

@flow(name="Customer Analytics Pipeline", log_prints=True)
def main_pipeline():
    print("🚀 Starting Customer Analytics Pipeline...")
    generate_data()
    load_to_duckdb()
    run_segmentation()
    run_churn()
    run_forecast()
    generate_report()
    print("✅ Pipeline complete! Report saved to reports/output/")

if __name__ == "__main__":
    main_pipeline()