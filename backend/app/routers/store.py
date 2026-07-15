"""Store profile endpoints: list/get/create/update the current user's store.

Enforces "1 user = 1 store" by rejecting a second store creation when one
already exists for the user.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.auth import AuthContext, get_ctx
from app.models import Store
from app.schemas import StoreCreate, StoreRead, StoreStatus, StoreUpdate

router = APIRouter(prefix="/api/store", tags=["store"])


@router.get("", response_model=StoreStatus)
def get_current_store(ctx: AuthContext = Depends(get_ctx)) -> StoreStatus:
    """Return the current user's store, or `{has_store: false}` if none yet.

    The frontend uses this to decide whether to show the onboarding flow.
    """
    if ctx.store is None:
        return StoreStatus(has_store=False, store=None)
    return StoreStatus(has_store=True, store=StoreRead.model_validate(ctx.store))


@router.post("", response_model=StoreRead, status_code=201)
def create_store(body: StoreCreate, ctx: AuthContext = Depends(get_ctx)) -> Store:
    """Create a store for the current user. Enforces the 1:1 rule by rejecting
    when the user already owns one."""
    existing = ctx.session.exec(
        select(Store).where(Store.owner_id == ctx.user.id)
    ).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Anda sudah memiliki toko. Satu pengguna hanya boleh memiliki satu toko.",
        )

    store = Store(
        owner_id=ctx.user.id,
        owner_name=ctx.user.name or "",
        name=body.name,
        category=body.category,
        currency=body.currency,
        default_language=body.default_language,
        notes=body.notes,
    )
    ctx.session.add(store)
    ctx.session.commit()
    ctx.session.refresh(store)
    return store


@router.patch("", response_model=StoreRead)
def update_store(body: StoreUpdate, ctx: AuthContext = Depends(get_ctx)) -> Store:
    """Update the current user's store fields."""
    store = ctx.require_store()
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(store, key, value)
    ctx.session.add(store)
    ctx.session.commit()
    ctx.session.refresh(store)
    return store