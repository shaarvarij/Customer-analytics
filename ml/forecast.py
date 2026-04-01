import duckdb
import pandas as pd
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')

DB_PATH = "data/analytics.db"

def run_forecast():
    con = duckdb.connect(DB_PATH)

    df = con.execute("""
        SELECT order_date AS ds, revenue AS y
        FROM daily_revenue
        ORDER BY order_date
    """).df()

    df['ds'] = pd.to_datetime(df['ds'])

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        interval_width=0.95
    )
    model.fit(df)

    future   = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    forecast_out = forecast[['ds','yhat','yhat_lower','yhat_upper']].tail(30)
    forecast_out.columns = ['date','predicted_revenue','lower_bound','upper_bound']

    con.execute("""
        CREATE OR REPLACE TABLE revenue_forecast AS
        SELECT * FROM forecast_out
    """)

    total = forecast_out['predicted_revenue'].sum()
    print(f"✓ 30-day revenue forecast: ${total:,.0f}")
    print("✓ Forecast complete → revenue_forecast table")
    con.close()

if __name__ == "__main__":
    run_forecast()