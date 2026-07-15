"""Endpoints for the income/expense ledger."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlmodel import select

from app import services
from app.auth import AuthContext, get_ctx
from app.models import Transaction
from app.schemas import TransactionCreate, TransactionRead

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    limit: int = Query(default=50, le=500),
    ctx: AuthContext = Depends(get_ctx),
) -> list[Transaction]:
    store_id = ctx.require_store_id()
    return list(
        ctx.session.exec(
            select(Transaction)
            .where(Transaction.store_id == store_id)
            .order_by(Transaction.created_at.desc())  # type: ignore[attr-defined]
            .limit(limit)
        ).all()
    )


@router.post("", response_model=TransactionRead, status_code=201)
def create_transaction(
    body: TransactionCreate,
    ctx: AuthContext = Depends(get_ctx),
) -> Transaction:
    """Manually add a ledger entry; routes through the shared services layer so
    stock is kept in sync for sales/purchases."""
    store_id = ctx.require_store_id()
    if body.kind == "income":
        return services.record_sale(
            ctx.session,
            store_id,
            product_name=body.product_name,
            quantity=body.quantity or 1.0,
            amount=body.amount,
            unit=body.unit,
            description=body.description,
        )
    return services.record_expense(
        ctx.session,
        store_id,
        amount=body.amount,
        category=body.category or "operasional",
        description=body.description,
        product_name=body.product_name,
        quantity=body.quantity,
        unit=body.unit,
    )