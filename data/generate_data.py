import pandas as pd
import json
import random
from faker import Faker
from datetime import datetime, timedelta
import os

fake = Faker()
random.seed(42)
Faker.seed(42)

# ── Config ──────────────────────────────────────────
NUM_CUSTOMERS = 2000
NUM_ORDERS    = 10000
NUM_PRODUCTS  = 40
NUM_EVENTS    = 50000

PRODUCTS = [
    {"product_id": f"P{i:03d}", "name": fake.bs().title()[:30],
     "category": random.choice(["Electronics","Clothing","Home","Sports","Books"]),
     "price": round(random.uniform(5, 500), 2)}
    for i in range(1, NUM_PRODUCTS + 1)
]

# ── Customers ────────────────────────────────────────
def generate_customers():
    customers = []
    for i in range(1, NUM_CUSTOMERS + 1):
        signup = fake.date_between(start_date="-3y", end_date="-30d")
        customers.append({
            "customer_id":  f"C{i:04d}",
            "name":         fake.name(),
            "email":        fake.email(),
            "city":         fake.city(),
            "country":      fake.country_code(),
            "signup_date":  signup.isoformat(),
            "segment":      random.choice(["Premium","Standard","Basic"]),
        })
    df = pd.DataFrame(customers)
    df.to_csv("data/customers.csv", index=False)
    print(f"✓ {len(df)} customers → data/customers.csv")

# ── Orders ───────────────────────────────────────────
def generate_orders():
    orders = []
    customer_ids = [f"C{i:04d}" for i in range(1, NUM_CUSTOMERS + 1)]
    for i in range(1, NUM_ORDERS + 1):
        product   = random.choice(PRODUCTS)
        qty       = random.randint(1, 5)
        order_date = fake.date_between(start_date="-2y", end_date="today")
        orders.append({
            "order_id":    f"O{i:05d}",
            "customer_id": random.choice(customer_ids),
            "product_id":  product["product_id"],
            "quantity":    qty,
            "unit_price":  product["price"],
            "total_amount": round(product["price"] * qty, 2),
            "order_date":  order_date.isoformat(),
            "status":      random.choice(["completed","completed","completed","returned","cancelled"]),
        })
    with open("data/orders.json", "w") as f:
        json.dump(orders, f, indent=2)
    print(f"✓ {len(orders)} orders → data/orders.json")

# ── Website events ───────────────────────────────────
def generate_events():
    import pyarrow as pa
    import pyarrow.parquet as pq

    customer_ids = [f"C{i:04d}" for i in range(1, NUM_CUSTOMERS + 1)]
    event_types  = ["page_view","add_to_cart","purchase","search","product_view"]
    events = []
    base = datetime.now() - timedelta(days=365)
    for i in range(NUM_EVENTS):
        ts = base + timedelta(seconds=random.randint(0, 365*24*3600))
        events.append({
            "event_id":    f"E{i:06d}",
            "customer_id": random.choice(customer_ids),
            "event_type":  random.choice(event_types),
            "page":        random.choice(["/home","/products","/cart","/checkout","/account"]),
            "timestamp":   ts.isoformat(),
            "session_id":  fake.uuid4(),
        })
    table = pa.Table.from_pydict({k: [e[k] for e in events] for k in events[0]})
    pq.write_table(table, "data/events.parquet")
    print(f"✓ {len(events)} events → data/events.parquet")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    generate_customers()
    generate_orders()
    generate_events()
    print("\n✅ All data generated successfully!")