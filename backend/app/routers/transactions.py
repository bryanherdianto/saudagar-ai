"""Endpoints for the income/expense ledger."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app import services
from app.database import get_session
from app.models import Transaction
from app.schemas import TransactionCreate, TransactionRead

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    limit: int = Query(default=50, le=500),
    session: Session = Depends(get_session),
) -> list[Transaction]:
    return session.exec(
        select(Transaction).order_by(Transaction.created_at.desc()).limit(limit)
    ).all()


@router.post("", response_model=TransactionRead, status_code=201)
def create_transaction(
    body: TransactionCreate, session: Session = Depends(get_session)
) -> Transaction:
    """Manually add a ledger entry; routes through the shared services layer so
    stock is kept in sync for sales/purchases."""
    if body.kind == "income":
        return services.record_sale(
            session,
            product_name=body.product_name,
            quantity=body.quantity or 1.0,
            amount=body.amount,
            unit=body.unit,
            description=body.description,
        )
    return services.record_expense(
        session,
        amount=body.amount,
        category=body.category or "operasional",
        description=body.description,
        product_name=body.product_name,
        quantity=body.quantity,
        unit=body.unit,
    )
