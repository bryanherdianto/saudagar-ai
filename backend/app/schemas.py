"""Pydantic request/response schemas for the API surface."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# --- Products ---
class ProductCreate(BaseModel):
    name: str
    sku: str | None = None
    category: str = ""
    unit: str = "pcs"
    price: float = 0.0
    cost: float = 0.0
    stock: float = 0.0
    low_stock_threshold: float = 5.0
    description: str = ""


class ProductUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    unit: str | None = None
    price: float | None = None
    cost: float | None = None
    stock: float | None = None
    low_stock_threshold: float | None = None
    description: str | None = None


class ProductRead(BaseModel):
    id: int
    name: str
    sku: str | None
    category: str
    unit: str
    price: float
    cost: float
    stock: float
    low_stock_threshold: float
    description: str
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Transactions ---
class TransactionCreate(BaseModel):
    kind: str = Field(description="income | expense")
    category: str = ""
    description: str = ""
    amount: float = 0.0
    quantity: float = 0.0
    unit: str = ""
    product_name: str = ""


class TransactionRead(BaseModel):
    id: int
    kind: str
    category: str
    description: str
    amount: float
    quantity: float
    unit: str
    product_name: str
    source: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Chat / Assistant ---
class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str
    actions: list[str] = []  # human-readable summary of tool actions taken
    ai_enabled: bool = True


# --- Insights (dashboard narrative) ---
class InsightResponse(BaseModel):
    headline: str
    narrative: str
    recommendations: list[str]
    metrics: dict
    ai_enabled: bool = True


# --- Catalog generator ---
class CatalogRequest(BaseModel):
    product_name: str
    details: str = ""  # optional extra selling points / description
    languages: list[str] = ["id", "en"]
    tone: str = "persuasive"


class CatalogItem(BaseModel):
    language: str
    title: str
    description: str


class CatalogResponse(BaseModel):
    items: list[CatalogItem]
    ai_enabled: bool = True


# --- Customer service / sales engine ---
class CustomerServiceRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class CustomerServiceResponse(BaseModel):
    reply: str
    suggested_upsell: str | None = None
    ai_enabled: bool = True


# --- Store profile ---
class StoreCreate(BaseModel):
    name: str
    category: str = ""
    currency: str = "IDR"
    default_language: str = "id"
    notes: str = ""


class StoreUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    currency: str | None = None
    default_language: str | None = None
    notes: str | None = None


class StoreRead(BaseModel):
    id: int
    name: str
    owner_id: int | None
    owner_name: str
    category: str
    currency: str
    default_language: str
    notes: str
    created_at: datetime

    class Config:
        from_attributes = True


class StoreStatus(BaseModel):
    """Lightweight response for the 'has_store?' check."""
    has_store: bool
    store: StoreRead | None = None


# --- Telegram integration ---
class TelegramLinkResponse(BaseModel):
    """Returned by POST /api/integrations/telegram/link - everything the
    frontend needs to open the deep link and start the connect flow."""
    bot_username: str
    deep_link: str
    expires_at: datetime


class TelegramStatusResponse(BaseModel):
    """Returned by GET /api/integrations/telegram/status - whether the
    signed-in user's store is currently linked to a Telegram chat."""
    connected: bool
    telegram_username: str | None = None
    connected_at: datetime | None = None


class UserRead(BaseModel):
    id: int
    clerk_user_id: str
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
