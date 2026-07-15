"""Application configuration loaded from environment variables.

All settings are read from environment variables (or a local `.env` file).
See `.env.example` for the full list of supported keys.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    app_name: str = "Saudagar.ai"
    environment: str = "development"

    # --- Database ---
    # Default to a local SQLite file so the app runs with zero setup.
    database_url: str = "sqlite:///./saudagar.db"

    # --- Google Gemini / LangChain ---
    # When empty, the backend runs in "mock" mode with deterministic,
    # rule-based responses so you can develop the UI without a key.
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "models/text-embedding-004"
    llm_temperature: float = 0.3

# --- CORS ---
    # Comma-separated lists of allowed origins for the Next.js frontend.
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # --- Clerk (auth) ---
    # The Clerk issuer/instance domain used to discover the JWKS endpoint and
    # verify JWTs sent by the frontend. Set this to your Clerk Frontend API
    # domain (e.g. "https://saudagar.clerk.accounts.dev").
    # When empty, auth is DISABLED — every route is treated as the bootstrap
    # user (dev/demo only). Configure before allowing real users.
    clerk_issuer: str = ""
    # Optional override of the JWKS URL (defaults to f"{clerk_issuer}/.well-known/jwks.json")
    clerk_jwks_url: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def ai_enabled(self) -> bool:
        """True when a real Gemini key is configured."""
        return bool(self.gemini_api_key.strip())

    @property
    def auth_enabled(self) -> bool:
        """True when Clerk verification is configured. When False, the backend
        runs in a single-tenant demo mode using a bootstrap user."""
        return bool(self.clerk_issuer.strip())

    @property
    def jwks_url(self) -> str:
        return self.clerk_jwks_url.strip() or f"{self.clerk_issuer.rstrip('/')}/.well-known/jwks.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
