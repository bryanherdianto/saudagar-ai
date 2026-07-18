"""Database models for Saudagar.ai.

A small multi-tenant schema: each Clerk-authenticated user owns exactly one
store (enforced at the API layer; the FK is designed as 1:N for forward
compatibility). Products and transactions are scoped to a store via a
`store_id` foreign key so two merchants never share data.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel, UniqueConstraint


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
    # Which channel produced this row: "manual" | "dashboard" | "assistant"
    # | "telegram" | "whatsapp". Gives merchants auditability when the AI acts
    # outside the dashboard.
    source: str = "manual"
    created_at: datetime = Field(default_factory=_utcnow, index=True)


# --------------------------------------------------------------------------
# Telegram integration
# --------------------------------------------------------------------------
class TelegramConnection(SQLModel, table=True):
    """Links a Telegram chat to a store. This is the bridge that lets the bot
    resolve an incoming `chat_id` back to the shared `store_id`, so Telegram
    and the dashboard act on exactly the same catalog/stock/ledger.

    One active connection per chat AND per store (a chat talks to one store,
    a store is driven by one chat) — enforced by unique constraints below.
    """

    __table_args__ = (
        UniqueConstraint("telegram_chat_id", name="uq_telegram_chat"),
        UniqueConstraint("store_id", name="uq_telegram_store"),
    )

    id: int | None = Field(default=None, primary_key=True)
    store_id: int = Field(foreign_key="store.id", index=True)
    telegram_chat_id: int = Field(index=True)
    telegram_username: str = ""  # @handle, best-effort (may be empty)
    connected_at: datetime = Field(default_factory=_utcnow)
    is_active: bool = True


class TelegramLinkToken(SQLModel, table=True):
    """A short-lived, single-use token minted by the dashboard so a Clerk user
    can prove ownership of the store when they tap `/start link_<token>` in
    Telegram. Never guessable (secrets.token_urlsafe) and expires quickly."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    store_id: int = Field(foreign_key="store.id", index=True)
    token: str = Field(index=True, unique=True)
    expires_at: datetime
    used_at: datetime | None = None
    created_at: datetime = Field(default_factory=_utcnow)


class ConversationMessage(SQLModel, table=True):
    """Short-term chat memory for channels that can't hold history themselves.

    The dashboard keeps its history in the browser and sends it with each
    /api/chat call; Telegram has no such client state, so we retain the most
    recent exchanges per (store, channel) here and prune the rest. Kept
    separate per channel on purpose — a Telegram conversation never leaks
    into the dashboard chat window, while both act on the same store data.
    """

    id: int | None = Field(default=None, primary_key=True)
    store_id: int = Field(foreign_key="store.id", index=True)
    channel: str = Field(default="telegram", index=True)  # "telegram" | "whatsapp"
    role: str  # "user" | "assistant"
    content: str = ""
    created_at: datetime = Field(default_factory=_utcnow, index=True)


class ProcessedWebhookEvent(SQLModel, table=True):
    """Idempotency ledger. Telegram retries a webhook until it gets a 200, so
    we record each `update_id` here BEFORE recording finance so a replayed
    update can never double-book a sale. `external_event_id` is unique per
    platform."""

    __table_args__ = (
        UniqueConstraint(
            "platform", "external_event_id", name="uq_webhook_event"
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    platform: str = Field(default="telegram", index=True)
    external_event_id: str = Field(index=True)  # Telegram update_id (as str)
    processed_at: datetime = Field(default_factory=_utcnow)