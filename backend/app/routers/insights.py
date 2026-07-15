"""Dashboard analytics narrative endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.ai.analyst import generate_insights
from app.auth import AuthContext, get_ctx
from app.config import settings
from app.schemas import InsightResponse

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("", response_model=InsightResponse)
def insights(
    days: int = Query(default=7, ge=1, le=90),
    ctx: AuthContext = Depends(get_ctx),
) -> InsightResponse:
    store_id = ctx.require_store_id()
    data = generate_insights(ctx.session, store_id, days)
    return InsightResponse(**data, ai_enabled=settings.ai_enabled)