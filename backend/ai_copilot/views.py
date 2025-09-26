"""
AI Copilot Views

Strict, database-only Q&A for Supply Chain using Supabase (SQL + vector search).
- No hallucinations: answers must cite retrieved rows; otherwise reply with insufficiency message.
- Wired endpoints: inventory, orders, risk, analytics via explicit SQL or RPC.
- Clear documentation blocks explain retrieval, ranking, and response construction.

Environment:
- SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY (service key required for RLS bypass server-side)
- OPENAI/HF for embeddings only (optional), never used to fabricate facts beyond retrieved data

"""
import os
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

# Optional LLM libs for embeddings only
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_EMBED_MODEL = os.getenv("COPILOT_EMBED_MODEL", "text-embedding-3-small")

# Supabase client
from supabase import create_client, Client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------------------------------------------------------
# Utility: Safe vector embeddings (optional)
# -----------------------------------------------------------------------------

def get_embedding(text: str) -> Optional[List[float]]:
    """
    Return embedding vector for text. If no provider configured, return None.
    Embeddings are used ONLY for retrieval; never for generating facts.
    """
    if not OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        e = client.embeddings.create(model=DEFAULT_EMBED_MODEL, input=text)
        return e.data[0].embedding  # type: ignore
    except Exception:
        return None

# -----------------------------------------------------------------------------
# Retrieval Layer for Supply Chain
# -----------------------------------------------------------------------------
# All factual data comes from Supabase tables and SQL functions. If retrieval
# returns no evidence, responses must indicate insufficient data.

@dataclass
class RetrievalResult:
    source: str
    rows: List[Dict[str, Any]]
    query_ms: float


def run_sql(sql: str, params: Optional[Dict[str, Any]] = None) -> RetrievalResult:
    """
    Execute parameterized SQL via Supabase PostgREST RPC or raw SQL (via rest/rpc).
    Falls back to table select patterns when needed.
    """
    if not supabase:
        return RetrievalResult(source="supabase", rows=[], query_ms=0)
    start = time.time()
    # Supabase Python client does not support raw SQL directly; expect SQL encapsulated
    # in Postgres functions exposed as RPC. If plain selects are detected, try to parse
    # route to table queries. Lightweight router below handles common cases.
    rows: List[Dict[str, Any]] = []
    try:
        sql_l = sql.strip().lower()
        if sql_l.startswith("select") and " from inventory" in sql_l:
            # naive router for inventory view
            table = "inventory"
            q = supabase.table(table).select("*")
            if params and "sku" in params:
                q = q.eq("sku", params["sku"])  # type: ignore
            if params and "limit" in params:
                q = q.limit(int(params["limit"]))  # type: ignore
            data = q.execute().data
            rows = data or []
        elif sql_l.startswith("select") and " from orders" in sql_l:
            table = "orders"
            q = supabase.table(table).select("*")
            if params and "order_id" in params:
                q = q.eq("id", params["order_id"])  # type: ignore
            if params and "status" in params:
                q = q.eq("status", params["status"])  # type: ignore
            if params and "limit" in params:
                q = q.limit(int(params["limit"]))  # type: ignore
            data = q.execute().data
            rows = data or []
        elif sql_l.startswith("select") and " from risk_events" in sql_l:
            table = "risk_events"
            q = supabase.table(table).select("*")
            if params and "severity" in params:
                q = q.gte("severity", params["severity"])  # type: ignore
            if params and "since" in params:
                q = q.gte("event_time", params["since"])  # type: ignore
            data = q.execute().data
            rows = data or []
        elif sql_l.startswith("select") and " from analytics_metrics" in sql_l:
            table = "analytics_metrics"
            q = supabase.table(table).select("*")
            if params and "metric" in params:
                q = q.eq("metric", params["metric"])  # type: ignore
            if params and "since" in params:
                q = q.gte("ts", params["since"])  # type: ignore
            data = q.execute().data
            rows = data or []
        else:
            # Attempt RPC if provided
            fn = params.get("rpc") if params else None
            if fn:
                res = supabase.rpc(fn, params.get("args", {})).execute()
                rows = res.data or []
    except Exception:
        rows = []
    return RetrievalResult(source="supabase", rows=rows, query_ms=(time.time() - start) * 1000)


def vector_search(query: str, top_k: int = 8, threshold: float = 0.15) -> RetrievalResult:
    """
    Perform semantic search over embeddings table (supply_chain_embeddings) using
    cosine similarity computed in SQL (requires a Postgres function or pgvector index).
    Assumes a view or RPC 'match_embeddings' exists. If missing, returns empty.
    """
    if not supabase:
        return RetrievalResult(source="vector", rows=[], query_ms=0)
    start = time.time()
    rows: List[Dict[str, Any]] = []
    vec = get_embedding(query)
    if not vec:
        return RetrievalResult(source="vector", rows=[], query_ms=(time.time() - start) * 1000)
    try:
        # Expect a Postgres RPC: match_embeddings(query_embedding, top_k, threshold)
        payload = {
            "query_embedding": vec,
            "match_count": top_k,
            "threshold": threshold,
        }
        res = supabase.rpc("match_embeddings", payload).execute()
        rows = res.data or []
    except Exception:
        rows = []
    return RetrievalResult(source="vector", rows=rows, query_ms=(time.time() - start) * 1000)

# -----------------------------------------------------------------------------
# Response Construction with Strict Non-hallucination
# -----------------------------------------------------------------------------

def format_answer(question: str, evidences: List[RetrievalResult]) -> Dict[str, Any]:
    """
    Build an answer solely from evidence rows. If no rows, return insufficiency.
    Include citations and the exact origin tables/ids used.
    """
    total_rows = sum(len(e.rows) for e in evidences)
    if total_rows == 0:
        return {
            "answer": "Insufficient data in supply chain database to answer. Please refine your query.",
            "citations": [],
            "sources": [e.source for e in evidences],
        }

    snippets: List[str] = []
    citations: List[Dict[str, Any]] = []

    for ev in evidences:
        for row in ev.rows:
            # Create compact human-readable snippets
            key_fields = []
            for k in ["sku", "id", "order_no", "status", "quantity", "location", "metric", "value", "severity"]:
                if k in row and row[k] is not None:
                    key_fields.append(f"{k}={row[k]}")
            if key_fields:
                snippets.append("; ".join(key_fields))
            citations.append({"source": ev.source, "row": row})

    # Aggregate into answer text
    answer = "Based on Supabase data: " + "; ".join(snippets[:10])
    return {
        "answer": answer,
        "citations": citations,
        "sources": [e.source for e in evidences],
    }

# -----------------------------------------------------------------------------
# Views
# -----------------------------------------------------------------------------

class CopilotChatView(APIView):
    permission_classes = [AllowAny]

    """
    Copilot chat that ONLY answers from Supabase supply chain DB via:
    - SQL table queries: inventory, orders, risk_events, analytics_metrics
    - Vector search: supply_chain_embeddings via RPC 'match_embeddings'
    If retrieval yields nothing, returns an insufficiency message. No free-form LLM.

    Request schema:
    { "question": str, "filters": {optional}, "top_k": int? }
    Response schema:
    { "answer": str, "citations": list, "sources": list, "retrieval_ms": float }
    """

    def post(self, request):
        start = time.time()
        body = request.data or {}
        question: str = (body.get("question") or "").strip()
        filters: Dict[str, Any] = body.get("filters") or {}
        top_k: int = int(body.get("top_k") or 8)

        # Simple intent routing to supply chain domains
        intents: List[Tuple[str, str, Dict[str, Any]]] = []
        ql = question.lower()
        if any(w in ql for w in ["stock", "inventory", "sku", "warehouse", "on hand", "reorder"]):
            intents.append(("inventory", "select * from inventory", {**filters, "limit": top_k}))
        if any(w in ql for w in ["order", "fulfill", "shipment", "backorder", "eta", "delivery"]):
            intents.append(("orders", "select * from orders", {**filters, "limit": top_k}))
        if any(w in ql for w in ["risk", "disruption", "delay", "incident", "alert"]):
            intents.append(("risk_events", "select * from risk_events", {**filters}))
        if any(w in ql for w in ["kpi", "metric", "fill rate", "otif", "forecast", "trend", "analytics"]):
            intents.append(("analytics_metrics", "select * from analytics_metrics", {**filters}))

        # Always attempt vector search for semantic grounding
        evidences: List[RetrievalResult] = []
        evidences.append(vector_search(question, top_k=min(top_k, 10)))
        for domain, sql, params in intents:
            ev = run_sql(sql, params)
            ev.source = domain
            evidences.append(ev)

        answer = format_answer(question, evidences)
        total_ms = round((time.time() - start) * 1000, 2)
        answer["retrieval_ms"] = total_ms
        return Response(answer, status=status.HTTP_200_OK)


class InventoryView(APIView):
    permission_classes = [AllowAny]
    """Inventory endpoint backed strictly by Supabase inventory table."""

    def get(self, request):
        sku = request.query_params.get("sku")
        limit = int(request.query_params.get("limit") or 100)
        sql = "select * from inventory"
        params = {"sku": sku, "limit": limit}
        ev = run_sql(sql, params)
        return Response({"rows": ev.rows, "query_ms": ev.query_ms}, status=status.HTTP_200_OK)


class OrdersView(APIView):
    permission_classes = [AllowAny]
    """Orders endpoint backed strictly by Supabase orders table."""

    def get(self, request):
        order_id = request.query_params.get("order_id")
        status_f = request.query_params.get("status")
        limit = int(request.query_params.get("limit") or 100)
        sql = "select * from orders"
        params = {"order_id": order_id, "status": status_f, "limit": limit}
        ev = run_sql(sql, params)
        return Response({"rows": ev.rows, "query_ms": ev.query_ms}, status=status.HTTP_200_OK)


class RiskView(APIView):
    permission_classes = [AllowAny]
    """Risk events endpoint backed strictly by Supabase risk_events table."""

    def get(self, request):
        severity = request.query_params.get("severity")
        since = request.query_params.get("since")
        sql = "select * from risk_events"
        params = {"severity": severity, "since": since}
        ev = run_sql(sql, params)
        return Response({"rows": ev.rows, "query_ms": ev.query_ms}, status=status.HTTP_200_OK)


class AnalyticsView(APIView):
    permission_classes = [AllowAny]
    """Analytics metrics endpoint backed strictly by Supabase analytics_metrics table."""

    def get(self, request):
        metric = request.query_params.get("metric")
        since = request.query_params.get("since")
        sql = "select * from analytics_metrics"
        params = {"metric": metric, "since": since}
        ev = run_sql(sql, params)
        return Response({"rows": ev.rows, "query_ms": ev.query_ms}, status=status.HTTP_200_OK)


# -----------------------------------------------------------------------------
# Documentation block: AI data retrieval logic
# -----------------------------------------------------------------------------
"""
AI Retrieval Logic (Supply Chain Only)

1) Input Parsing
   - Extract 'question' and optional 'filters'.
   - Derive domain intents (inventory, orders, risk, analytics) via keyword routing.

2) Retrieval
   - Execute SQL table queries via Supabase for each relevant domain.
   - Perform semantic vector search via RPC 'match_embeddings' using OpenAI embeddings if available.

3) Evidence Consolidation
   - Combine rows from all retrievals; compute compact snippets for answer.

4) Strict Answering
   - If no rows found, respond with insufficiency message; NO LLM generation.
   - Otherwise, answer is a structured summary of retrieved rows with citations.

5) Safety and Scope
   - Facts must come from Supabase tables (inventory, orders, risk_events, analytics_metrics) or embeddings matches.
   - Never fabricate values; do not infer beyond rows. Include row-level citation objects.
"""
