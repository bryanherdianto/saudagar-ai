"""Telegram webhook receiver.

Telegram calls POST /webhooks/telegram for every update. This router:

  1. verifies the shared secret header (rejects spoofed calls),
  2. ignores unsupported updates (photos, status events, non-text),
  3. dedupes by `update_id` BEFORE any finance work (retry-safe),
  4. handles `/start link_<token>` account linking, and
  5. for normal messages, resolves the store and calls the SAME internal
     `run_assistant()` the dashboard uses — never the /api/chat HTTP route.

The endpoint is a sync path operation so FastAPI runs it in a worker thread;
that keeps the blocking DB + LLM work off the event loop.
"""

from __future__ import annotations

import logging
import secrets

from fastapi import APIRouter, Body, Depends, Header, HTTPException, status
from sqlmodel import Session

from app.ai.agent import run_assistant
from app.config import settings
from app.database import get_session
from app.services import telegram as telegram_service

logger = logging.getLogger("saudagar.telegram")

router = APIRouter(prefix="/webhooks/telegram", tags=["webhooks"])

# Reply copy (Bahasa Indonesia)
_NOT_LINKED = (
    "Halo! Nomor Telegram ini belum terhubung ke toko mana pun.\n\n"
    "Buka dashboard Saudagar.ai, masuk ke Pengaturan → Telegram, lalu klik "
    "\"Hubungkan Telegram\" untuk menautkan akun Anda."
)
_LINK_INVALID = (
    "Tautan penghubung tidak valid atau sudah kedaluwarsa. "
    "Silakan buat tautan baru dari dashboard Saudagar.ai."
)
_GENERIC_START = (
    "Selamat datang di Saudagar.ai! Untuk mulai, hubungkan akun ini dari "
    "dashboard Anda (Pengaturan → Telegram)."
)


def _verify_secret(header_value: str | None) -> None:
    """Reject the request unless the secret header matches our configured one.

    Telegram echoes `X-Telegram-Bot-Api-Secret-Token` (the value we set when
    registering the webhook). A missing/empty configured secret is treated as
    a misconfiguration and blocks all calls rather than leaving an open hook.
    """
    expected = settings.telegram_webhook_secret.strip()
    if not expected:
        logger.error("TELEGRAM_WEBHOOK_SECRET is not set — refusing webhook calls")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    if not header_value or not secrets.compare_digest(header_value, expected):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


def _extract_text_message(update: dict) -> tuple[int, int, str, str] | None:
    """Pull (update_id, chat_id, text, username) from a text-message update.

    Returns None for updates we don't handle yet (photos, edits, join/leave
    status events, callbacks, …) so the caller can ack them with 200 and move
    on — Telegram must get a 200 or it keeps retrying.
    """
    update_id = update.get("update_id")
    message = update.get("message")
    if update_id is None or not isinstance(message, dict):
        return None
    text = message.get("text")
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    if not isinstance(text, str) or chat_id is None:
        return None
    username = (message.get("from") or {}).get("username") or ""
    return int(update_id), int(chat_id), text, username


@router.post("")
def telegram_webhook(
    update: dict = Body(default={}),
    x_telegram_secret: str | None = Header(
        default=None, alias="X-Telegram-Bot-Api-Secret-Token"
    ),
    session: Session = Depends(get_session),
) -> dict:
    _verify_secret(x_telegram_secret)

    extracted = _extract_text_message(update)
    if extracted is None:
        # Unsupported update type — acknowledge so Telegram stops retrying.
        return {"ok": True, "ignored": True}
    update_id, chat_id, text, username = extracted

    # Idempotency: claim the update before doing anything that writes finance.
    # A duplicate delivery (Telegram retry) is acked without re-processing.
    if not telegram_service.claim_event(session, update_id):
        logger.info("Duplicate Telegram update_id=%s ignored", update_id)
        return {"ok": True, "duplicate": True}

    stripped = text.strip()

    # --- Account linking: /start link_<token> ---
    if stripped.startswith("/start"):
        payload = stripped[len("/start"):].strip()
        if payload.startswith(telegram_service.LINK_PREFIX):
            raw_token = payload[len(telegram_service.LINK_PREFIX):]
            store = telegram_service.consume_link_token(
                session, raw_token, chat_id, username
            )
            if store is None:
                telegram_service.send_message(chat_id, _LINK_INVALID)
            else:
                telegram_service.send_message(
                    chat_id, f"Telegram berhasil terhubung ke toko {store.name}. "
                    "Sekarang Anda bisa mencatat penjualan dan mengecek stok dari sini."
                )
            return {"ok": True}
        # Plain /start with no linking payload.
        telegram_service.send_message(chat_id, _GENERIC_START)
        return {"ok": True}

    # --- Normal message: route to the shared AI on the linked store ---
    store_id = telegram_service.resolve_store_id(session, chat_id)
    if store_id is None:
        telegram_service.send_message(chat_id, _NOT_LINKED)
        return {"ok": True}

    # Load the store's recent Telegram exchanges as context (kept separate
    # from the dashboard's browser-held history — see ConversationMessage).
    history = telegram_service.get_history(session, store_id)
    try:
        reply, _actions, _ai_enabled = run_assistant(
            session, store_id, text, history=history, source="telegram"
        )
    except Exception as exc:
        logger.exception("run_assistant failed for chat_id=%s: %s", chat_id, exc)
        reply = "Maaf, terjadi kendala saat memproses pesan Anda. Coba lagi sebentar lagi."
    else:
        telegram_service.append_history(session, store_id, text, reply)

    telegram_service.send_message(chat_id, reply)
    return {"ok": True}
