import duckdb
import pandas as pd
import numpy as np
from datetime import datetime
import os

DB_PATH = "data/analytics.db"

def run_segmentation():
    con = duckdb.connect(DB_PATH)

    df = con.execute("""
        SELECT
            customer_id,
            total_orders,
            total_spent,
            last_order_date,
            first_order_date
        FROM customer_order_summary
    """).df()

    today = datetime.today()
    df['last_order_date']  = pd.to_datetime(df['last_order_date'])
    df['first_order_date'] = pd.to_datetime(df['first_order_date'])

    # RFM scores
    df['recency']   = (today - df['last_order_date']).dt.days
    df['frequency'] = df['total_orders']
    df['monetary']  = df['total_spent']

    df['R'] = pd.qcut(df['recency'],   q=4, labels=[4,3,2,1]).astype(int)
    df['F'] = pd.qcut(df['frequency'].rank(method='first'), q=4, labels=[1,2,3,4]).astype(int)
    df['M'] = pd.qcut(df['monetary'].rank(method='first'),  q=4, labels=[1,2,3,4]).astype(int)
    df['rfm_score'] = df['R'] + df['F'] + df['M']

    def segment(score):
        if score >= 10: return 'Champion'
        elif score >= 7: return 'Loyal'
        elif score >= 5: return 'At Risk'
        else:            return 'Lost'

    df['segment'] = df['rfm_score'].apply(segment)

    con.execute("""
        CREATE OR REPLACE TABLE customer_segments AS
        SELECT * FROM df
    """)

    counts = df['segment'].value_counts()
    for seg, count in counts.items():
        print(f"  {seg}: {count} customers")

    con.close()
    print("✓ Segmentation complete → customer_segments table")

if __name__ == "__main__":
    run_segmentation()