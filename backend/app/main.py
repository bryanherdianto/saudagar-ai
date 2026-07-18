"""FastAPI application entrypoint for Saudagar.ai."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import (
    catalog,
    chat,
    cs,
    insights,
    integrations,
    products,
    store,
    telegram,
    transactions,
    user,
)
from app.seed import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_if_empty()
    yield


app = FastAPI(
    title="Saudagar.ai API",
    description="Asisten usaha dagang pintar — FastAPI + LangChain + Gemini.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(cs.router)
app.include_router(insights.router)
app.include_router(catalog.router)
app.include_router(products.router)
app.include_router(transactions.router)
app.include_router(store.router)
app.include_router(user.router)
app.include_router(integrations.router)
app.include_router(telegram.router)


@app.get("/", tags=["health"])
def root() -> dict:
    return {
        "name": settings.app_name,
        "status": "ok",
        "ai_enabled": settings.ai_enabled,
        "auth_enabled": settings.auth_enabled,
        "model": settings.gemini_model if settings.ai_enabled else None,
        "docs": "/docs",
    }


@app.get("/api/health", tags=["health"])
def health() -> dict:
    return {
        "status": "ok",
        "ai_enabled": settings.ai_enabled,
        "auth_enabled": settings.auth_enabled,
        "telegram_enabled": settings.telegram_enabled,
    }
