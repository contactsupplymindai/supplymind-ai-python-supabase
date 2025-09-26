"""
Seed demo data for AI supply chain platform into Supabase.
Creates: suppliers, items, inventory, orders, risk_events, analytics_metrics, chat_logs, and embeddings (optional).

Usage:
  SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... python scripts/seed_demo.py
"""
import os
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

assert SUPABASE_URL and SUPABASE_KEY, "Missing Supabase env vars"
client = create_client(SUPABASE_URL, SUPABASE_KEY)

now = datetime.utcnow()

suppliers = [
    {"id": 1, "name": "Acme Components", "region": "NA", "rating": 4.5},
    {"id": 2, "name": "Globex Manufacturing", "region": "EU", "rating": 4.2},
    {"id": 3, "name": "Initech Parts", "region": "APAC", "rating": 4.0},
]

items = [
    {"sku": "SKU-1001", "name": "Widget A", "supplier_id": 1},
    {"sku": "SKU-1002", "name": "Widget B", "supplier_id": 2},
    {"sku": "SKU-1003", "name": "Widget C", "supplier_id": 3},
]

inventory = [
    {"sku": "SKU-1001", "location": "WH1", "quantity": 120},
    {"sku": "SKU-1001", "location": "WH2", "quantity": 60},
    {"sku": "SKU-1002", "location": "WH1", "quantity": 25},
    {"sku": "SKU-1003", "location": "WH3", "quantity": 0},
]

orders = []
for i in range(1, 11):
    orders.append({
        "id": i,
        "order_no": f"ORD-{1000+i}",
        "sku": random.choice(items)["sku"],
        "quantity": random.randint(1, 50),
        "status": random.choice(["created", "allocated", "shipped", "delivered", "backorder"]),
        "eta": (now + timedelta(days=random.randint(1, 14))).isoformat(),
    })

risk_events = [
    {"id": 1, "type": "port_delay", "severity": 0.6, "event_time": (now - timedelta(days=2)).isoformat(), "region": "APAC"},
    {"id": 2, "type": "weather", "severity": 0.8, "event_time": (now - timedelta(days=1)).isoformat(), "region": "EU"},
]

analytics_metrics = []
for d in range(14):
    ts = (now - timedelta(days=d)).isoformat()
    analytics_metrics.append({"metric": "fill_rate", "ts": ts, "value": round(0.9 - d*0.005, 3)})
    analytics_metrics.append({"metric": "otif", "ts": ts, "value": round(0.88 - d*0.004, 3)})

chat_logs = [
    {"session_id": 1, "role": "user", "content": "What is on-hand for SKU-1001?", "ts": now.isoformat()},
    {"session_id": 1, "role": "assistant", "content": "Based on DB: SKU-1001 WH1=120; WH2=60", "ts": now.isoformat()},
]

def upsert(table: str, rows: List[Dict[str, Any]], on_conflict: str):
    if not rows:
        return
    print(f"Upserting {len(rows)} rows into {table}...")
    client.table(table).upsert(rows, on_conflict=on_conflict).execute()


def main():
    upsert("suppliers", suppliers, on_conflict="id")
    upsert("items", items, on_conflict="sku")
    upsert("inventory", inventory, on_conflict="sku,location")
    upsert("orders", orders, on_conflict="id")
    upsert("risk_events", risk_events, on_conflict="id")
    upsert("analytics_metrics", analytics_metrics, on_conflict="metric,ts")
    upsert("chat_logs", chat_logs, on_conflict="session_id,ts")
    print("Seed complete.")

if __name__ == "__main__":
    main()
