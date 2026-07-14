"""Auto customer-service + sales engine endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.ai.analyst import generate_cs_reply
from app.config import settings
from app.database import get_session
from app.schemas import CustomerServiceRequest, CustomerServiceResponse

router = APIRouter(prefix="/api/cs", tags=["customer-service"])


@router.post("", response_model=CustomerServiceResponse)
def customer_service(
    body: CustomerServiceRequest, session: Session = Depends(get_session)
) -> CustomerServiceResponse:
    reply, upsell = generate_cs_reply(session, body.message, body.history)
    return CustomerServiceResponse(
        reply=reply, suggested_upsell=upsell, ai_enabled=settings.ai_enabled
    )
