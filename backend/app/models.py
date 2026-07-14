"""Database models for Saudagar.ai.

A deliberately small schema for the MVP: a single store profile, a product
catalog (stock), and a ledger of income/expense transactions.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Store(SQLModel, table=True):
    """The merchant's business profile — used as RAG grounding context."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    owner_name: str = ""
    category: str = ""  # e.g. "Warung Makan", "Toko Kelontong"
    currency: str = "IDR"
    default_language: str = "id"
    notes: str = ""  # freeform store rules the AI should respect
    created_at: datetime = Field(default_factory=_utcnow)


class Product(SQLModel, table=True):
    """A catalog item with its current stock level and price."""

    id: int | None = Field(default=None, primary_key=True)
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
    """A single income or expense entry in the ledger."""

    id: int | None = Field(default=None, primary_key=True)
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
