"""Gemini chat + embedding model factories via langchain-google-genai.

Both factories return `None` when no API key is configured, allowing the rest
of the app to fall back to deterministic, rule-based behaviour so the project
runs end-to-end without a key.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.config import settings


@lru_cache
def get_llm() -> Any | None:
    """Return a configured ChatGoogleGenerativeAI, or None in mock mode."""
    if not settings.ai_enabled:
        return None

    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=settings.llm_temperature,
    )


@lru_cache
def get_embeddings() -> Any | None:
    """Return configured Gemini embeddings, or None in mock mode."""
    if not settings.ai_enabled:
        return None

    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    return GoogleGenerativeAIEmbeddings(
        model=settings.gemini_embedding_model,
        google_api_key=settings.gemini_api_key,
    )
