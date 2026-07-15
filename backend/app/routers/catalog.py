"""Multi-language catalog / copywriting generator."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.ai.analyst import generate_catalog
from app.auth import AuthContext, get_ctx
from app.config import settings
from app.schemas import CatalogRequest, CatalogResponse

router = APIRouter(prefix="/api/catalog", tags=["catalog"])


@router.post("/generate", response_model=CatalogResponse)
def generate(body: CatalogRequest, ctx: AuthContext = Depends(get_ctx)) -> CatalogResponse:
    items = generate_catalog(body.product_name, body.details, body.languages, body.tone)
    return CatalogResponse(items=items, ai_enabled=settings.ai_enabled)


@router.post("/generate-with-image", response_model=CatalogResponse)
async def generate_with_image(
    ctx: AuthContext = Depends(get_ctx),
    product_name: str = Form(...),
    details: str = Form(""),
    languages: str = Form("id,en"),
    tone: str = Form("persuasive"),
    image: UploadFile | None = File(default=None),
) -> CatalogResponse:
    """Same as /generate but accepts an optional product photo (multipart).

    The image is accepted so the frontend upload flow works end-to-end; the
    filename is folded into the details as an extra hint for the copywriter.
    """
    langs = [lang.strip() for lang in languages.split(",") if lang.strip()]
    extra = details
    if image is not None:
        extra = f"{details} (foto produk: {image.filename})".strip()
    items = generate_catalog(product_name, extra, langs, tone)
    return CatalogResponse(items=items, ai_enabled=settings.ai_enabled)