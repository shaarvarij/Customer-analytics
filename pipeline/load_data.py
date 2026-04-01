import duckdb
import json
import os

DB_PATH = "data/analytics.db"

def get_connection():
    return duckdb.connect(DB_PATH)

def load_customers(con):
    con.execute("""
        CREATE OR REPLACE TABLE customers AS
        SELECT * FROM read_csv_auto('data/customers.csv')
    """)
    count = con.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    print(f"✓ Loaded {count} customers")

def load_orders(con):
    con.execute("""
        CREATE OR REPLACE TABLE orders AS
        SELECT * FROM read_json_auto('data/orders.json')
    """)
    count = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    print(f"✓ Loaded {count} orders")

def load_events(con):
    con.execute("""
        CREATE OR REPLACE TABLE events AS
        SELECT * FROM read_parquet('data/events.parquet')
    """)
    count = con.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    print(f"✓ Loaded {count} events")

def load_products(con):
    con.execute("""
        CREATE OR REPLACE TABLE products AS
        SELECT * FROM read_csv_auto('data/customers.csv') LIMIT 0
    """)
    # Load products from the generated list
    import sys
    sys.path.insert(0, 'data')
    from generate_data import PRODUCTS
    import pandas as pd
    df = pd.DataFrame(PRODUCTS)
    con.execute("CREATE OR REPLACE TABLE products AS SELECT * FROM df")
    count = con.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    print(f"✓ Loaded {count} products")

def create_summary_views(con):
    con.execute("""
        CREATE OR REPLACE VIEW customer_order_summary AS
        SELECT
            c.customer_id,
            c.name,
            c.email,
            c.segment,
            c.signup_date,
            COUNT(o.order_id)        AS total_orders,
            SUM(o.total_amount)      AS total_spent,
            MAX(o.order_date)        AS last_order_date,
            MIN(o.order_date)        AS first_order_date
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.status = 'completed'
        GROUP BY ALL
    """)
    print("✓ Created customer_order_summary view")

    con.execute("""
        CREATE OR REPLACE VIEW daily_revenue AS
        SELECT
            order_date,
            COUNT(order_id)      AS num_orders,
            SUM(total_amount)    AS revenue,
            AVG(total_amount)    AS avg_order_value
        FROM orders
        WHERE status = 'completed'
        GROUP BY order_date
        ORDER BY order_date
    """)
    print("✓ Created daily_revenue view")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    con = get_connection()
    load_customers(con)
    load_orders(con)
    load_events(con)
    load_products(con)
    create_summary_views(con)
    con.close()
    print("\n✅ All data loaded into DuckDB successfully!")