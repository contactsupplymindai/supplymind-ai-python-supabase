"""
Core ORM-style base models and mixins for SupplyMind AI microservices.

These models are designed to mirror the public Supabase (Postgres) schema and
provide type hints, validation, and serialization helpers that are framework
agnostic. They can be used with:
- direct async SQL (e.g., with asyncpg/psycopg)
- Supabase Python client (postgrest) for CRUD
- lightweight ORMs (SQLModel/SQLAlchemy) by mapping fields as needed

Notes:
- UUIDs are used as primary identifiers to align with Supabase defaults.
- TimestampMixin manages created_at/updated_at at the application layer; in DB,
  migrations should set DEFAULT now() and triggers for updated_at if desired.
- Validation is performed via pydantic BaseModel; runtime use is optional but
  recommended at service boundaries.

"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID, uuid4

try:
    from pydantic import BaseModel as PydBaseModel, Field, field_validator, model_validator
except Exception:  # fallback if pydantic not installed during type-check
    # Minimal shims to keep type checking friendly without runtime dependency
    class PydBaseModel:  # type: ignore
        pass

    def Field(*args: Any, **kwargs: Any) -> Any:  # type: ignore
        return None

    def field_validator(*args: Any, **kwargs: Any):  # type: ignore
        def dec(fn):
            return fn
        return dec

    def model_validator(*args: Any, **kwargs: Any):  # type: ignore
        def dec(fn):
            return fn
        return dec


# ---------------------------------------------------------------------------
# Mixins
# ---------------------------------------------------------------------------
class TimestampMixin(PydBaseModel):
    """Common timestamp fields.

    Database (Supabase) recommended columns:
    - created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    - updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
      with trigger to set updated_at = now() on UPDATE
    """

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def _ensure_ordering(self) -> "TimestampMixin":
        # Ensure updated_at >= created_at for sanity (does not mutate DB)
        if self.updated_at < self.created_at:
            object.__setattr__(self, "updated_at", self.created_at)
        return self


class SoftDeleteMixin(PydBaseModel):
    """Soft delete support.

    Database column: deleted_at TIMESTAMPTZ NULL
    Records with deleted_at IS NOT NULL are considered soft-deleted.
    """

    deleted_at: Optional[datetime] = None

    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class TenantMixin(PydBaseModel):
    """Multi-tenant separation by organization/project."""

    tenant_id: UUID


class OwnedByUserMixin(PydBaseModel):
    """Denormalized owner reference for quick filters."""

    owner_user_id: Optional[UUID] = None


# ---------------------------------------------------------------------------
# Base entities
# ---------------------------------------------------------------------------
class User(TimestampMixin, PydBaseModel):
    """Represents an application user; pairs with Supabase auth.users via id.

    Table: public.users (application profile layer)
    """

    id: UUID = Field(default_factory=uuid4)
    auth_user_id: Optional[UUID] = None  # Reference to auth.users.id if used
    email: Optional[str] = None
    display_name: Optional[str] = None
    role: Optional[Literal[
        "admin",
        "analyst",
        "operator",
        "viewer",
        "supplier",
    ]] = None
    is_active: bool = True
    last_login_at: Optional[datetime] = None


class Supplier(TimestampMixin, TenantMixin, PydBaseModel):
    """Suppliers table mirrors external vendor partners."""

    id: UUID = Field(default_factory=uuid4)
    name: str
    code: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    active: bool = True


class InventoryItem(TimestampMixin, TenantMixin, PydBaseModel):
    """Stock keeping units and current levels."""

    id: UUID = Field(default_factory=uuid4)
    sku: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    supplier_id: Optional[UUID] = None
    unit_of_measure: Literal[
        "each",
        "box",
        "case",
        "kg",
        "lb",
        "l",
        "m",
    ] = "each"
    unit_cost: Optional[float] = Field(default=None, ge=0)
    unit_price: Optional[float] = Field(default=None, ge=0)
    quantity_on_hand: int = Field(default=0, ge=0)
    reorder_point: Optional[int] = Field(default=None, ge=0)
    reorder_quantity: Optional[int] = Field(default=None, ge=0)
    location: Optional[str] = None
    lot_number: Optional[str] = None
    expiration_date: Optional[datetime] = None


class InventoryTxn(TimestampMixin, TenantMixin, OwnedByUserMixin, PydBaseModel):
    """Inventory movement transactions (receipts, issues, adjustments)."""

    id: UUID = Field(default_factory=uuid4)
    item_id: UUID
    txn_type: Literal["receipt", "issue", "adjustment", "transfer"]
    quantity: int
    source_location: Optional[str] = None
    dest_location: Optional[str] = None
    reference: Optional[str] = None  # e.g., PO number, SO number
    notes: Optional[str] = None

    @field_validator("quantity")
    @classmethod
    def _non_zero(cls, v: int) -> int:
        if v == 0:
            raise ValueError("quantity cannot be zero")
        return v


class PurchaseOrder(TimestampMixin, TenantMixin, OwnedByUserMixin, PydBaseModel):
    """Purchase orders to suppliers."""

    id: UUID = Field(default_factory=uuid4)
    order_number: str
    supplier_id: UUID
    status: Literal[
        "draft",
        "submitted",
        "confirmed",
        "partially_received",
        "received",
        "cancelled",
    ] = "draft"
    currency: Literal["USD", "EUR", "GBP", "JPY", "CNY", "INR", "AUD", "CAD"] = "USD"
    expected_receipt_at: Optional[datetime] = None
    subtotal: float = Field(ge=0, default=0)
    tax: float = Field(ge=0, default=0)
    shipping: float = Field(ge=0, default=0)
    discount: float = Field(ge=0, default=0)
    total: float = Field(ge=0, default=0)
    notes: Optional[str] = None


class PurchaseOrderLine(PydBaseModel):
    id: UUID = Field(default_factory=uuid4)
    purchase_order_id: UUID
    item_id: UUID
    quantity: int = Field(ge=1)
    unit_cost: float = Field(ge=0)
    expected_at: Optional[datetime] = None


class SalesOrder(TimestampMixin, TenantMixin, OwnedByUserMixin, PydBaseModel):
    """Customer orders."""

    id: UUID = Field(default_factory=uuid4)
    order_number: str
    customer_id: Optional[UUID] = None
    status: Literal[
        "draft",
        "confirmed",
        "allocated",
        "picked",
        "shipped",
        "invoiced",
        "cancelled",
    ] = "draft"
    currency: Literal["USD", "EUR", "GBP", "JPY", "CNY", "INR", "AUD", "CAD"] = "USD"
    promised_ship_at: Optional[datetime] = None
    subtotal: float = Field(ge=0, default=0)
    tax: float = Field(ge=0, default=0)
    shipping: float = Field(ge=0, default=0)
    discount: float = Field(ge=0, default=0)
    total: float = Field(ge=0, default=0)
    notes: Optional[str] = None


class SalesOrderLine(PydBaseModel):
    id: UUID = Field(default_factory=uuid4)
    sales_order_id: UUID
    item_id: UUID
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0)
    promised_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Risk and analytics
# ---------------------------------------------------------------------------
class RiskEvent(TimestampMixin, TenantMixin, PydBaseModel):
    """Discrete risk events captured for supplier, item, or external signals."""

    id: UUID = Field(default_factory=uuid4)
    scope_type: Literal["supplier", "item", "global", "logistics"]
    scope_id: Optional[UUID] = None  # when not global
    severity: Literal["low", "medium", "high", "critical"]
    category: Literal[
        "quality",
        "delivery",
        "financial",
        "geopolitical",
        "regulatory",
        "environmental",
        "cyber",
        "demand",
        "supply",
    ]
    probability: float = Field(ge=0, le=1)
    impact_score: float = Field(ge=0)
    description: Optional[str] = None
    source: Optional[str] = None  # e.g., news url, system, auditor
    detected_by: Optional[str] = None  # model name, analyst, integration


class SupplierKPI(TimestampMixin, TenantMixin, PydBaseModel):
    """Daily/weekly KPIs per supplier for analytics and trend modeling."""

    id: UUID = Field(default_factory=uuid4)
    supplier_id: UUID
    kpi_date: datetime
    on_time_delivery_rate: Optional[float] = Field(default=None, ge=0, le=1)
    defect_rate: Optional[float] = Field(default=None, ge=0, le=1)
    lead_time_days: Optional[float] = Field(default=None, ge=0)
    fulfillment_rate: Optional[float] = Field(default=None, ge=0, le=1)
    backlog_orders: Optional[int] = Field(default=None, ge=0)


class InventoryForecast(TimestampMixin, TenantMixin, PydBaseModel):
    """Forecasted demand/supply for an item."""

    id: UUID = Field(default_factory=uuid4)
    item_id: UUID
    horizon_days: int = Field(ge=1)
    method: Literal["arima", "prophet", "lstm", "xgboost", "ewma", "baseline"] = "baseline"
    point_forecast: float
    p10: Optional[float] = None
    p50: Optional[float] = None
    p90: Optional[float] = None
    version: Optional[str] = None


class AnomalyDetection(TimestampMixin, TenantMixin, PydBaseModel):
    """Anomaly detections on metrics (inventory, orders, supplier KPIs)."""

    id: UUID = Field(default_factory=uuid4)
    entity_type: Literal["inventory", "sales_order", "purchase_order", "supplier", "kpi"]
    entity_id: UUID
    metric: str  # e.g., quantity_on_hand, lead_time_days
    value: float
    zscore: Optional[float] = None
    window: Optional[int] = None
    flagged: bool = True


# ---------------------------------------------------------------------------
# Utility DTOs and helpers
# ---------------------------------------------------------------------------
class PageRequest(PydBaseModel):
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
    order_by: Optional[str] = None
    order_dir: Literal["asc", "desc"] = "asc"


class PageResult(PydBaseModel):
    items: List[Dict[str, Any]]
    total: int
    limit: int
    offset: int


# ---------------------------------------------------------------------------
# Supabase table name mapping (for convenience in repositories)
# ---------------------------------------------------------------------------
SUPABASE_TABLES = {
    "users": "users",
    "suppliers": "suppliers",
    "inventory_items": "inventory_items",
    "inventory_txns": "inventory_txns",
    "purchase_orders": "purchase_orders",
    "purchase_order_lines": "purchase_order_lines",
    "sales_orders": "sales_orders",
    "sales_order_lines": "sales_order_lines",
    "risk_events": "risk_events",
    "supplier_kpis": "supplier_kpis",
    "inventory_forecasts": "inventory_forecasts",
    "anomalies": "anomalies",
}


__all__ = [
    # Mixins
    "TimestampMixin",
    "SoftDeleteMixin",
    "TenantMixin",
    "OwnedByUserMixin",
    # Entities
    "User",
    "Supplier",
    "InventoryItem",
    "InventoryTxn",
    "PurchaseOrder",
    "PurchaseOrderLine",
    "SalesOrder",
    "SalesOrderLine",
    # Risk & Analytics
    "RiskEvent",
    "SupplierKPI",
    "InventoryForecast",
    "AnomalyDetection",
    # DTOs
    "PageRequest",
    "PageResult",
    # Helpers
    "SUPABASE_TABLES",
]
