import duckdb
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

DB_PATH = "data/analytics.db"

def run_churn_prediction():
    con = duckdb.connect(DB_PATH)

    df = con.execute("""
        SELECT
            s.customer_id,
            s.recency,
            s.frequency,
            s.monetary,
            s.rfm_score,
            s.R, s.F, s.M
        FROM customer_segments s
    """).df()

    # Label: churned if recency > 90 days
    df['churned'] = (df['recency'] > 90).astype(int)

    features = ['recency', 'frequency', 'monetary', 'rfm_score', 'R', 'F', 'M']
    X = df[features]
    y = df['churned']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("Model performance:")
    print(classification_report(y_test, y_pred))

    # Predict on all customers
    df['churn_probability'] = model.predict_proba(X)[:, 1]
    df['churn_risk'] = pd.cut(
        df['churn_probability'],
        bins=[0, 0.3, 0.6, 1.0],
        labels=['Low', 'Medium', 'High']
    )

    con.execute("""
        CREATE OR REPLACE TABLE churn_predictions AS
        SELECT
            customer_id,
            recency,
            frequency,
            monetary,
            churn_probability,
            churn_risk,
            churned AS already_churned
        FROM df
    """)

    high_risk = len(df[df['churn_risk'] == 'High'])
    print(f"✓ {high_risk} high-risk customers flagged")
    print("✓ Churn prediction complete → churn_predictions table")

    con.close()

if __name__ == "__main__":
    run_churn_prediction()