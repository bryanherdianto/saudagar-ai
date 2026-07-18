"""The natural-language assistant endpoint (the 'WhatsApp bot' brain)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.ai.agent import run_assistant
from app.auth import AuthContext, get_ctx
from app.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["assistant"])


@router.post("", response_model=ChatResponse)
def chat(body: ChatRequest, ctx: AuthContext = Depends(get_ctx)) -> ChatResponse:
    store_id = ctx.require_store_id()
    reply, actions, ai_enabled = run_assistant(
        ctx.session, store_id, body.message, body.history, source="dashboard"
    )
    return ChatResponse(reply=reply, actions=actions, ai_enabled=ai_enabled)