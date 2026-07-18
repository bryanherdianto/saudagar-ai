"""Telegram integration service.

Everything the Telegram channel needs that isn't an HTTP route lives here:

- sending replies via the Bot API,
- minting and consuming short-lived account-linking tokens,
- resolving an incoming chat_id back to the shared `store_id`,
- webhook idempotency (dedupe by Telegram `update_id`).

Kept separate from the routers so the webhook stays thin and the business
logic is unit-testable. All store-scoped reads/writes go through the same
`store_id` key the dashboard uses, so both channels act on one dataset.
"""

from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.config import settings
from app.models import (
    ConversationMessage,
    ProcessedWebhookEvent,
    Store,
    TelegramConnection,
    TelegramLinkToken,
)
from app.schemas import ChatMessage

logger = logging.getLogger("saudagar.telegram")

# Prefix used in the deep-link start payload: t.me/<bot>?start=link_<token>
LINK_PREFIX = "link_"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_aware(dt: datetime) -> datetime:
    """SQLite round-trips datetimes as naive; treat them as UTC for compares."""
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


# --------------------------------------------------------------------------
# Sending messages
# --------------------------------------------------------------------------
def send_message(chat_id: int, text: str) -> bool:
    """Send a text reply to a chat via the Bot API. Returns True on success.

    Synchronous on purpose: the webhook handler is a sync path operation that
    FastAPI runs in a worker thread, so a blocking call here does not stall
    the event loop. Never raises — failures are logged and reported via the
    return value so one bad send can't 500 the webhook (which would make
    Telegram retry the whole update)."""
    if not settings.telegram_enabled:
        logger.warning("send_message called but TELEGRAM_BOT_TOKEN is not set")
        return False
    try:
        resp = httpx.post(
            f"{settings.telegram_api_url}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10.0,
        )
        resp.raise_for_status()
        return True
    except Exception as exc:  # network/HTTP errors — log without the token
        logger.error("Failed to send Telegram message to %s: %s", chat_id, exc)
        return False


# --------------------------------------------------------------------------
# Account linking
# --------------------------------------------------------------------------
def create_link_token(session: Session, user_id: int, store_id: int) -> TelegramLinkToken:
    """Mint a fresh single-use linking token for a user's store."""
    token = secrets.token_urlsafe(24)
    expires_at = _utcnow() + timedelta(minutes=settings.telegram_link_token_ttl_minutes)
    row = TelegramLinkToken(
        user_id=user_id,
        store_id=store_id,
        token=token,
        expires_at=expires_at,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def build_deep_link(token: str) -> str:
    """Build the t.me deep link the user taps to open the bot pre-filled."""
    return f"https://t.me/{settings.telegram_bot_username}?start={LINK_PREFIX}{token}"


def consume_link_token(
    session: Session,
    raw_token: str,
    telegram_chat_id: int,
    telegram_username: str = "",
) -> Store | None:
    """Redeem a linking token and bind this chat to the token's store.

    Returns the linked `Store` on success, or None when the token is unknown,
    already used, or expired. Idempotent-ish: re-binding the same chat to the
    same store just refreshes the existing connection.
    """
    token = session.exec(
        select(TelegramLinkToken).where(TelegramLinkToken.token == raw_token)
    ).first()
    if token is None or token.used_at is not None:
        return None
    if _as_aware(token.expires_at) < _utcnow():
        return None

    store = session.get(Store, token.store_id)
    if store is None:
        return None

    # Upsert the connection. A store has at most one active connection; if the
    # merchant re-links from a different chat, point the store at the new chat.
    conn = session.exec(
        select(TelegramConnection).where(
            TelegramConnection.store_id == token.store_id
        )
    ).first()
    if conn is None:
        conn = TelegramConnection(
            store_id=token.store_id,
            telegram_chat_id=telegram_chat_id,
            telegram_username=telegram_username,
        )
    else:
        conn.telegram_chat_id = telegram_chat_id
        conn.telegram_username = telegram_username
        conn.connected_at = _utcnow()
        conn.is_active = True
    session.add(conn)

    token.used_at = _utcnow()
    session.add(token)
    session.commit()
    return store


def resolve_store_id(session: Session, telegram_chat_id: int) -> int | None:
    """Map an incoming Telegram chat to its store, or None if unlinked."""
    conn = session.exec(
        select(TelegramConnection).where(
            TelegramConnection.telegram_chat_id == telegram_chat_id,
            TelegramConnection.is_active == True,  # noqa: E712
        )
    ).first()
    return conn.store_id if conn else None


def get_status(session: Session, store_id: int) -> TelegramConnection | None:
    """Return the active connection for a store, if any."""
    return session.exec(
        select(TelegramConnection).where(
            TelegramConnection.store_id == store_id,
            TelegramConnection.is_active == True,  # noqa: E712
        )
    ).first()


def disconnect(session: Session, store_id: int) -> bool:
    """Remove the store's Telegram link (and its chat memory). Returns True
    if a connection existed."""
    conn = session.exec(
        select(TelegramConnection).where(
            TelegramConnection.store_id == store_id
        )
    ).first()
    if conn is None:
        return False
    session.delete(conn)
    # Drop the channel's conversation memory too — a future re-link (possibly
    # from a different Telegram account) should start with a clean slate.
    for row in session.exec(
        select(ConversationMessage).where(
            ConversationMessage.store_id == store_id,
            ConversationMessage.channel == "telegram",
        )
    ).all():
        session.delete(row)
    session.commit()
    return True


# --------------------------------------------------------------------------
# Conversation history (short-term memory per store+channel)
# --------------------------------------------------------------------------
# Keep the last N exchanges (user + assistant pairs) as model context, and
# prune the table so it never grows unbounded.
HISTORY_EXCHANGES = 8
_HISTORY_KEEP_ROWS = HISTORY_EXCHANGES * 2


def get_history(
    session: Session, store_id: int, channel: str = "telegram"
) -> list[ChatMessage]:
    """Return the most recent exchanges for a store+channel, oldest first."""
    rows = session.exec(
        select(ConversationMessage)
        .where(
            ConversationMessage.store_id == store_id,
            ConversationMessage.channel == channel,
        )
        .order_by(ConversationMessage.id.desc())  # type: ignore[union-attr]
        .limit(_HISTORY_KEEP_ROWS)
    ).all()
    return [
        ChatMessage(role=row.role, content=row.content)
        for row in reversed(rows)
    ]


def append_history(
    session: Session,
    store_id: int,
    user_text: str,
    assistant_text: str,
    channel: str = "telegram",
) -> None:
    """Store one exchange and prune rows beyond the retention window."""
    session.add(
        ConversationMessage(
            store_id=store_id, channel=channel, role="user", content=user_text
        )
    )
    session.add(
        ConversationMessage(
            store_id=store_id,
            channel=channel,
            role="assistant",
            content=assistant_text,
        )
    )
    session.commit()

    # Prune: delete everything older than the newest _HISTORY_KEEP_ROWS rows.
    rows = session.exec(
        select(ConversationMessage)
        .where(
            ConversationMessage.store_id == store_id,
            ConversationMessage.channel == channel,
        )
        .order_by(ConversationMessage.id.desc())  # type: ignore[union-attr]
        .offset(_HISTORY_KEEP_ROWS)
    ).all()
    if rows:
        for row in rows:
            session.delete(row)
        session.commit()


# --------------------------------------------------------------------------
# Webhook idempotency
# --------------------------------------------------------------------------
def claim_event(session: Session, update_id: int, platform: str = "telegram") -> bool:
    """Atomically claim a webhook event by its id.

    Returns True if this is the FIRST time we've seen this update (caller
    should process it), or False if it was already processed (caller should
    skip — this is a Telegram retry). We insert the marker BEFORE doing any
    finance work so a replay can never double-book a sale; the DB unique
    constraint makes the claim race-safe across workers.
    """
    row = ProcessedWebhookEvent(
        platform=platform, external_event_id=str(update_id)
    )
    session.add(row)
    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False
