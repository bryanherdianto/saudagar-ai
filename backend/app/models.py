"""Database models for Saudagar.ai.

A small multi-tenant schema: each Clerk-authenticated user owns exactly one
store (enforced at the API layer; the FK is designed as 1:N for forward
compatibility). Products and transactions are scoped to a store via a
`store_id` foreign key so two merchants never share data.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    """A Clerk-authenticated merchant. Bridge between Clerk's `sub` claim and
    the local DB row."""

    id: int | None = Field(default=None, primary_key=True)
    clerk_user_id: str = Field(index=True, unique=True)
    email: str = ""
    name: str = ""
    created_at: datetime = Field(default_factory=_utcnow)


class Store(SQLModel, table=True):
    """The merchant's business profile — used as RAG grounding context.

    `owner_id` is a FK to `user.id`. Multiple stores per user are allowed at
    the DB level (1:N) but the API enforces "max 1 store per user" for now.
    """

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    owner_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    owner_name: str = ""  # display label, kept in sync with the User's name
    category: str = ""  # e.g. "Warung Makan", "Toko Kelontong"
    currency: str = "IDR"
    default_language: str = "id"
    notes: str = ""  # freeform store rules the AI should respect
    created_at: datetime = Field(default_factory=_utcnow)


class Product(SQLModel, table=True):
    """A catalog item with its current stock level and price, scoped to a store."""

    id: int | None = Field(default=None, primary_key=True)
    store_id: int | None = Field(default=None, foreign_key="store.id", index=True)
    name: str = Field(index=True)
    sku: str | None = Field(default=None, index=True)
    category: str = ""
    unit: str = "pcs"  # porsi, kg, botol, ...
    price: float = 0.0  # selling price per unit
    cost: float = 0.0  # purchase cost per unit
    stock: float = 0.0
    low_stock_threshold: float = 5.0
    description: str = ""
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class Transaction(SQLModel, table=True):
    """A single income or expense entry in the ledger, scoped to a store."""

    id: int | None = Field(default=None, primary_key=True)
    store_id: int | None = Field(default=None, foreign_key="store.id", index=True)
    kind: str = Field(index=True)  # "income" | "expense"
    category: str = ""  # "penjualan", "pembelian stok", "operasional", ...
    description: str = ""
    amount: float = 0.0  # total value of the entry (positive number)
    quantity: float = 0.0
    unit: str = ""
    product_id: int | None = Field(default=None, foreign_key="product.id")
    product_name: str = ""
    source: str = "manual"  # "manual" | "assistant"
    created_at: datetime = Field(default_factory=_utcnow, index=True)