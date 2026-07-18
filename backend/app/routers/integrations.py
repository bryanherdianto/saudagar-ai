"""Protected account-linking endpoints for the dashboard.

These run behind Clerk auth (`get_ctx`), so the backend knows exactly which
user + store is creating a Telegram link. No Telegram credentials are ever
entered on the website — the merchant only taps a deep link.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import AuthContext, get_ctx
from app.config import settings
from app.schemas import TelegramLinkResponse, TelegramStatusResponse
from app.services import telegram as telegram_service

router = APIRouter(prefix="/api/integrations/telegram", tags=["integrations"])


def _require_telegram_enabled() -> None:
    if not settings.telegram_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Integrasi Telegram belum dikonfigurasi di server.",
        )


@router.post("/link", response_model=TelegramLinkResponse)
def create_link(ctx: AuthContext = Depends(get_ctx)) -> TelegramLinkResponse:
    """Mint a short-lived linking token and return a bot deep link."""
    _require_telegram_enabled()
    store = ctx.require_store()
    assert store.id is not None and ctx.user.id is not None
    token = telegram_service.create_link_token(ctx.session, ctx.user.id, store.id)
    return TelegramLinkResponse(
        bot_username=settings.telegram_bot_username,
        deep_link=telegram_service.build_deep_link(token.token),
        expires_at=token.expires_at,
    )


@router.get("/status", response_model=TelegramStatusResponse)
def link_status(ctx: AuthContext = Depends(get_ctx)) -> TelegramStatusResponse:
    """Report whether the signed-in user's store is linked to Telegram."""
    store_id = ctx.require_store_id()
    conn = telegram_service.get_status(ctx.session, store_id)
    if conn is None:
        return TelegramStatusResponse(connected=False)
    return TelegramStatusResponse(
        connected=True,
        telegram_username=conn.telegram_username or None,
        connected_at=conn.connected_at,
    )


@router.delete("/link", status_code=status.HTTP_200_OK)
def disconnect(ctx: AuthContext = Depends(get_ctx)) -> dict:
    """Disconnect the store's Telegram account."""
    store_id = ctx.require_store_id()
    removed = telegram_service.disconnect(ctx.session, store_id)
    return {"disconnected": removed}
