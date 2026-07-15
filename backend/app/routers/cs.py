"""Auto customer-service + sales engine endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.ai.analyst import generate_cs_reply
from app.auth import AuthContext, get_ctx
from app.config import settings
from app.schemas import CustomerServiceRequest, CustomerServiceResponse

router = APIRouter(prefix="/api/cs", tags=["customer-service"])


@router.post("", response_model=CustomerServiceResponse)
def customer_service(
    body: CustomerServiceRequest,
    ctx: AuthContext = Depends(get_ctx),
) -> CustomerServiceResponse:
    store_id = ctx.require_store_id()
    reply, upsell = generate_cs_reply(ctx.session, store_id, body.message, body.history)
    return CustomerServiceResponse(
        reply=reply, suggested_upsell=upsell, ai_enabled=settings.ai_enabled
    )