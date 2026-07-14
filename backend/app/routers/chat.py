"""The natural-language assistant endpoint (the 'WhatsApp bot' brain)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.ai.agent import run_assistant
from app.database import get_session
from app.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["assistant"])


@router.post("", response_model=ChatResponse)
def chat(body: ChatRequest, session: Session = Depends(get_session)) -> ChatResponse:
    reply, actions, ai_enabled = run_assistant(session, body.message, body.history)
    return ChatResponse(reply=reply, actions=actions, ai_enabled=ai_enabled)
