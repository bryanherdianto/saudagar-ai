"""User profile endpoint - returns the currently authenticated user."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.auth import AuthContext, get_ctx
from app.schemas import UserRead

router = APIRouter(prefix="/api/me", tags=["user"])


@router.get("", response_model=UserRead)
def me(ctx: AuthContext = Depends(get_ctx)) -> UserRead:
    return UserRead.model_validate(ctx.user)