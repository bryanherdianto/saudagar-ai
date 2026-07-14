"""Dashboard analytics narrative endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.ai.analyst import generate_insights
from app.config import settings
from app.database import get_session
from app.schemas import InsightResponse

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("", response_model=InsightResponse)
def insights(
    days: int = Query(default=7, ge=1, le=90),
    session: Session = Depends(get_session),
) -> InsightResponse:
    data = generate_insights(session, days)
    return InsightResponse(**data, ai_enabled=settings.ai_enabled)
