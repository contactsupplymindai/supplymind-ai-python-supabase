#!/usr/bin/env python3
"""
Enhanced demo seeding for SupplyMind
- Populates suppliers, products, inventory, orders, order_items, risk_events,
  document_embeddings, analytics_daily, analytics_kpis, and chat_logs
- Generates realistic relationships and time series
- Creates RAG demo docs, embeddings, and vector upserts
- Verifies via sample frontend-like queries

Usage:
  python scripts/enhanced_seed_demo.py

Env:
  SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
  OPENAI_API_KEY (optional for live embeddings; falls back to HF or fake)
  HUGGINGFACEHUB_API_TOKEN (optional)

Prereqs:
  pip install supabase numpy pandas faker tqdm httpx pydantic openai sentence-transformers
"""
import os
import random
import time
from datetime import datetime, timedelta
from uuid import uuid4
from typing import List, Dict, Any

import numpy as np
import pandas as pd
from faker import Faker
from tqdm import tqdm

# Supabase
from supabase import create_client, Client

# Embeddings: try OpenAI, fallback to HF, then random
EMBED_DIM = 768

fake = Faker()
random.seed(42)
np.random.seed(42)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
assert SUPABASE_URL and SUPABASE_KEY, "Missing Supabase env vars"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Try model providers
def embed_texts(texts: List[str]) -> List[List[float]]:
    # Prefer OpenAI text-embedding-3-large/mini
    try:
        from openai import OpenAI
        oai = OpenAI()
        model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
        resp = oai.embeddings.create(model=model, input=texts)
        return [d.embedding for d in resp.data]
    except Exception:
        pass
    # Fallback: HuggingFace sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer
        model_name = os.getenv("HF_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        m = SentenceTransformer(model_name)
        vecs = m.encode(texts, normalize_embeddings=True)
        return vecs.tolist()
    except Exception:
        pass
    # Last resort: random unit vectors
    vecs = np.random.randn(len(texts), EMBED_DIM)
    vecs = vecs / np.linalg.norm(vecs, axis=1, keepdims=True)
    return vecs.tolist()

# Utility insert in chunks
def insert_rows(table: str, rows: List[Dict[str, Any]], chunk: int = 500):
    for i in range(0, len(rows), chunk):
        batch = rows[i:i+chunk]
        res = supabase.table(table).upsert(batch).execute()
        if hasattr(res, 'error') and res.error:
            raise RuntimeError(f"Insert error into {table}: {res.error}")

# Clean tables (idempotent)
def truncate_tables():
    tables = [
        "chat_logs", "analytics_kpis", "analytics_daily", "document_embeddings",
        "risk_events", "order_items", "orders", "inventory", "products", "suppliers"
    ]
    for t in tables:
        try:
            supabase.rpc("truncate_table", {"t": t}).execute()
        except Exception:
            # if no RPC exists, try delete all
            supabase.table(t).delete().neq("id", None).execute()

# Generators
def gen_suppliers(n=8):
    rows = []
    industries = ["Electronics", "Automotive", "Pharma", "Food", "Textiles", "Logistics"]
    for i in range(n):
        sid = str(uuid4())
        rows.append({
            "id": sid,
            "name": f"{fake.company()} Supply Co.",
            "contact_email": fake.company_email(),
            "contact_phone": fake.phone_number(),
            "address": fake.address(),
            "industry": random.choice(industries),
            "risk_score": round(random.uniform(0, 100), 2),
            "on_time_delivery_rate": round(random.uniform(80, 99.5), 2),
            "quality_score": round(random.uniform(70, 99), 2),
            "created_at": datetime.utcnow().isoformat(),
        })
    return rows

def gen_products(suppliers, n_per=10):
    rows = []
    categories = ["CPU", "GPU", "Sensor", "Battery", "Display", "Packaging", "Raw Material"]
    for s in suppliers:
        for _ in range(n_per):
            pid = str(uuid4())
            rows.append({
                "id": pid,
                "supplier_id": s["id"],
                "sku": fake.unique.bothify(text="???-#####"),
                "name": f"{random.choice(categories)} {fake.color_name()}",
                "category": random.choice(categories),
                "unit_price": round(random.uniform(2, 800), 2),
                "lead_time_days": random.randint(3, 45),
                "min_order_qty": random.choice([10, 25, 50, 100]),
                "created_at": datetime.utcnow().isoformat(),
            })
    return rows

def gen_inventory(products):
    rows = []
    for p in products:
        rows.append({
            "id": str(uuid4()),
            "product_id": p["id"],
            "warehouse": random.choice(["EU-West", "US-East", "US-West", "APAC"]),
            "on_hand": random.randint(0, 5000),
            "on_order": random.randint(0, 3000),
            "safety_stock": random.randint(50, 500),
            "reorder_point": random.randint(80, 800),
            "updated_at": datetime.utcnow().isoformat(),
        })
    return rows

def gen_orders(products, days=120, avg_per_day=6):
    rows = []
    items = []
    start = datetime.utcnow() - timedelta(days=days)
    for d in range(days):
        date = start + timedelta(days=d)
        count = np.random.poisson(avg_per_day)
        for _ in range(count):
            oid = str(uuid4())
            status = random.choices(["pending","confirmed","shipped","delivered","canceled"],[0.1,0.25,0.25,0.35,0.05])[0]
            rows.append({
                "id": oid,
                "order_number": fake.unique.bothify(text="PO-########"),
                "order_date": date.isoformat(),
                "status": status,
                "created_at": date.isoformat(),
            })
            # items 1-5
            for _ in range(random.randint(1,5)):
                p = random.choice(products)
                qty = random.randint(1, 200)
                price = p["unit_price"]
                items.append({
                    "id": str(uuid4()),
                    "order_id": oid,
                    "product_id": p["id"],
                    "quantity": qty,
                    "unit_price": price,
                    "amount": round(qty*price, 2),
                })
    return rows, items

def gen_risk_events(suppliers, products, n=120):
    types = ["delay","quality_issue","shortage","regulatory","financial","geopolitical"]
    severities = ["low","medium","high","critical"]
    rows = []
    for _ in range(n):
        target = random.choice(["supplier","product"])
        if target == "supplier":
            ref_id = random.choice(suppliers)["id"]
        else:
            ref_id = random.choice(products)["id"]
        rows.append({
            "id": str(uuid4()),
            "target_type": target,
            "target_id": ref_id,
            "event_type": random.choice(types),
            "severity": random.choice(severities),
            "description": fake.paragraph(nb_sentences=3),
            "event_date": (datetime.utcnow() - timedelta(days=random.randint(0,180))).isoformat(),
            "created_at": datetime.utcnow().isoformat(),
        })
    return rows

def gen_docs_and_embeddings(suppliers, products):
    docs = []
    for s in suppliers:
        docs.append({
            "id": str(uuid4()),
            "doc_type": "supplier_profile",
            "source_id": s["id"],
            "title": f"Supplier Profile: {s['name']}",
            "content": f"Supplier {s['name']} in {s['industry']} with risk score {s['risk_score']}. {fake.paragraph(nb_sentences=6)}",
        })
    for p in products:
        docs.append({
            "id": str(uuid4()),
            "doc_type": "product_spec",
            "source_id": p["id"],
            "title": f"Spec Sheet: {p['name']}",
            "content": f"SKU {p['sku']} category {p['category']} lead time {p['lead_time_days']} days. {fake.paragraph(nb_sentences=6)}",
        })
    texts = [d["title"] + "\n" + d["content"] for d in docs]
    vecs = embed_texts(texts)
    rows = []
    for d, v in zip(docs, vecs):
        rows.append({
            "id": d["id"],
            "doc_type": d["doc_type"],
            "source_id": d["source_id"],
            "title": d["title"],
            "content": d["content"],
            "embedding": v,
            "created_at": datetime.utcnow().isoformat(),
        })
    return rows

def gen_analytics(orders, order_items):
    # daily revenue, units
    df = pd.DataFrame(order_items)
    # join with orders for date
    odf = pd.DataFrame(orders)[["id","order_date","status"]]
    m = df.merge(odf, left_on="order_id", right_on="id", how="left")
    m["date"] = pd.to_datetime(m["order_date"]).dt.date
    daily = m.groupby("date").agg(revenue=("amount","sum"), units=("quantity","sum")).reset_index()
    daily_rows = []
    for r in daily.itertuples():
        daily_rows.append({
            "id": str(uuid4()),
            "date": str(r.date),
            "metric": "revenue",
            "value": float(round(r.revenue, 2)),
        })
        daily_rows.append({
            "id": str(uuid4()),
            "date": str(r.date),
            "metric": "units",
            "value": int(r.units),
        })
    # KPIs snapshot
    kpi_rows = [
        {"id": str(uuid4()), "kpi": "gross_revenue_30d", "value": float(round(daily.tail(30)["revenue"].sum(),2))},
        {"id": str(uuid4()), "kpi": "units_30d", "value": int(daily.tail(30)["units"].sum())},
        {"id": str(uuid4()), "kpi": "avg_order_value_30d", "value": float(round(daily.tail(30)["revenue"].sum() / max(1,len(daily.tail(30))),2))},
    ]
    return daily_rows, kpi_rows

def gen_chat_logs(n=60):
    intents = [
        ("inventory_status", "What's the on-hand for GPU components?"),
        ("risk_query", "Show critical supplier risks this month."),
        ("order_eta", "When will PO-12345678 arrive?"),
        ("analytics", "Plot revenue last 30 days."),
        ("product_search", "Find sensors with lead time under 10 days."),
    ]
    rows = []
    for _ in range(n):
        intent, sample = random.choice(intents)
        rows.append({
            "id": str(uuid4()),
            "user_id": "demo-user",
            "role": "user",
            "message": sample,
            "intent": intent,
            "created_at": (datetime.utcnow() - timedelta(minutes=random.randint(0,60*72))).isoformat(),
        })
        rows.append({
            "id": str(uuid4()),
            "user_id": "demo-user",
            "role": "assistant",
            "message": fake.sentence(nb_words=18),
            "intent": intent,
            "created_at": datetime.utcnow().isoformat(),
        })
    return rows


def verify_frontend_queries():
    # mimic key UI queries
    checks = {}
    checks["suppliers_count"] = len(supabase.table("suppliers").select("id").execute().data)
    checks["products_count"] = len(supabase.table("products").select("id").execute().data)
    checks["orders_count"] = len(supabase.table("orders").select("id").execute().data)
    checks["risk_events_count"] = len(supabase.table("risk_events").select("id").execute().data)
    checks["embeddings_count"] = len(supabase.table("document_embeddings").select("id").execute().data)
    checks["analytics_points"] = len(supabase.table("analytics_daily").select("id").execute().data)
    checks["chat_logs"] = len(supabase.table("chat_logs").select("id").execute().data)
    # sample RAG search: cosine via Supabase pgvector
    try:
        query = "GPU lead time under 10 days"
        qvec = embed_texts([query])[0]
        res = supabase.rpc("match_documents", {"query_embedding": qvec, "match_threshold": 0.2, "match_count": 5}).execute()
        checks["rag_matches"] = len(getattr(res, 'data', []) or [])
    except Exception:
        checks["rag_matches"] = -1
    return checks


def main():
    print("Truncating existing demo data...")
    truncate_tables()

    print("Generating suppliers/products/inventory...")
    suppliers = gen_suppliers(10)
    products = gen_products(suppliers, n_per=12)
    inventory = gen_inventory(products)

    print("Generating orders and items...")
    orders, order_items = gen_orders(products, days=120, avg_per_day=8)

    print("Generating risk events...")
    risk_events = gen_risk_events(suppliers, products, n=160)

    print("Generating docs and embeddings...")
    doc_rows = gen_docs_and_embeddings(suppliers, products)

    print("Computing analytics...")
    daily_rows, kpi_rows = gen_analytics(orders, order_items)

    print("Generating chat logs...")
    chats = gen_chat_logs(80)

    print("Upserting data into Supabase...")
    insert_rows("suppliers", suppliers)
    insert_rows("products", products)
    insert_rows("inventory", inventory)
    insert_rows("orders", orders)
    insert_rows("order_items", order_items)
    insert_rows("risk_events", risk_events)
    insert_rows("document_embeddings", doc_rows)
    insert_rows("analytics_daily", daily_rows)
    insert_rows("analytics_kpis", kpi_rows)
    insert_rows("chat_logs", chats)

    print("Verifying frontend queries and RAG...")
    checks = verify_frontend_queries()
    for k, v in checks.items():
        print(f"{k}: {v}")

    print("Done. Demo data seeded and verified.")


if __name__ == "__main__":
    main()
