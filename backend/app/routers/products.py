"""CRUD endpoints for the product catalog / stock."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth import AuthContext, get_ctx
from app.models import Product
from app.schemas import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=list[ProductRead])
def list_products(ctx: AuthContext = Depends(get_ctx)) -> list[Product]:
    store_id = ctx.require_store_id()
    return list(
        ctx.session.exec(
            select(Product)
            .where(Product.store_id == store_id)
            .order_by(Product.name)
        ).all()
    )


@router.post("", response_model=ProductRead, status_code=201)
def create_product(body: ProductCreate, ctx: AuthContext = Depends(get_ctx)) -> Product:
    store_id = ctx.require_store_id()
    product = Product(**body.model_dump(), store_id=store_id)
    ctx.session.add(product)
    ctx.session.commit()
    ctx.session.refresh(product)
    return product


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int, body: ProductUpdate, ctx: AuthContext = Depends(get_ctx)
) -> Product:
    store_id = ctx.require_store_id()
    product = ctx.session.get(Product, product_id)
    if not product or product.store_id != store_id:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    ctx.session.add(product)
    ctx.session.commit()
    ctx.session.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(product_id: int, ctx: AuthContext = Depends(get_ctx)) -> dict:
    store_id = ctx.require_store_id()
    product = ctx.session.get(Product, product_id)
    if not product or product.store_id != store_id:
        raise HTTPException(status_code=404, detail="Product not found")
    ctx.session.delete(product)
    ctx.session.commit()
    return {"deleted": product_id}