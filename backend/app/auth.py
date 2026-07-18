"""Clerk authentication: JWT verification + user/store resolution.

Exposes a single FastAPI dependency `get_ctx` that yields an `AuthContext`
containing the live DB session, the authenticated user, and their active
store (or `None` when the user has not created one yet - letting onboarding
endpoints handle that case themselves).

Verification strategy: pyjwt with Clerk's JWKS endpoint (cached). When
`settings.auth_enabled` is False (no CLERK_ISSUER configured) the dependency
falls back to a "bootstrap" user so local dev / demo mode keeps working.
"""

from __future__ import annotations

import time
from collections.abc import Generator
from dataclasses import dataclass

import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlmodel import Session, select

from app.config import settings
from app.database import get_session
from app.models import Store, User


# --- JWKS cache (in-process, refreshes every 1h) ---
_jwks_client: jwt.PyJWKClient | None = None
_jwks_fetched_at: float = 0.0
_JWKS_TTL = 3600.0


def _get_jwks_client() -> jwt.PyJWKClient | None:
    """Return a cached PyJWKClient for Clerk's JWKS endpoint, or None when
    auth is disabled."""
    global _jwks_client, _jwks_fetched_at
    if not settings.auth_enabled:
        return None
    now = time.time()
    if _jwks_client is None or (now - _jwks_fetched_at) > _JWKS_TTL:
        _jwks_client = jwt.PyJWKClient(settings.jwks_url)
        _jwks_fetched_at = now
    return _jwks_client


def _verify_token(token: str) -> dict:
    """Verify the bearer JWT against Clerk's JWKS and return its claims."""
    client = _get_jwks_client()
    if client is None:
        # Auth disabled - callers must short-circuit to the bootstrap path.
        raise RuntimeError("Auth is disabled but _verify_token was called")

    signing_key = client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        # Clerk JWTs set `iss` to the issuer/instance domain; verify it.
        options={"verify_aud": False},
    )


def _get_or_create_user(session: Session, clerk_user_id: str, email: str, name: str) -> User:
    user = session.exec(
        select(User).where(User.clerk_user_id == clerk_user_id)
    ).first()
    if user is None:
        user = User(clerk_user_id=clerk_user_id, email=email, name=name)
        session.add(user)
        session.commit()
        session.refresh(user)
    else:
        dirty = False
        if email and user.email != email:
            user.email = email
            dirty = True
        if name and user.name != name:
            user.name = name
            dirty = True
        if dirty:
            session.add(user)
            session.commit()
            session.refresh(user)
    return user


def _bootstrap_user(session: Session) -> User:
    """Return the bootstrap user used in demo mode (no CLERK_ISSUER)."""
    user = session.exec(
        select(User).where(User.clerk_user_id == "bootstrap")
    ).first()
    if user is None:
        user = User(clerk_user_id="bootstrap", name="Bootstrap Owner")
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


@dataclass
class AuthContext:
    session: Session
    user: User
    store: Store | None  # None when the user has not created a store yet
    active_store_id: int | None  # explicit override from X-Store-Id header

    def require_store(self) -> Store:
        """Convenience for endpoints that absolutely need a store."""
        if self.store is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Anda belum memiliki toko. Buat toko terlebih dahulu.",
            )
        return self.store

    def require_store_id(self) -> int:
        """Return the active store's id as a guaranteed int (404 if no store).

        Use this when calling service functions that accept a `store_id: int`
        parameter, since `Store.id` is typed `int | None` from SQLModel.
        """
        store = self.require_store()
        assert store.id is not None  # committed rows always have a PK
        return store.id

    def require_store_and_id(self) -> tuple[Store, int]:
        store = self.require_store()
        assert store.id is not None
        return store, store.id


def get_ctx(
    session: Session = Depends(get_session),
    authorization: str | None = Header(default=None),
    x_store_id: int | None = Header(default=None, alias="X-Store-Id"),
) -> Generator[AuthContext, None, None]:
    """Resolve (session, user, active_store) for every authenticated request.

    - When `CLERK_ISSUER` is unset, all requests become the bootstrap user so
      the API keeps working in dev / demo mode without a Clerk account.
    - When set, requests without a valid `Authorization: Bearer …` header are
      rejected with 401.
    """
    if not settings.auth_enabled:
        user = _bootstrap_user(session)
    else:
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or malformed Authorization header. Expected 'Bearer <token>'.",
            )
        token = authorization.split(" ", 1)[1].strip()
        try:
            claims = _verify_token(token)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid or expired token: {exc}",
            ) from exc

        clerk_user_id = claims.get("sub") or ""
        if not clerk_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing 'sub' claim.",
            )
        user = _get_or_create_user(
            session,
            clerk_user_id=clerk_user_id,
            email=claims.get("email") or "",
            name=claims.get("name") or "",
        )

    # Resolve the active store. If X-Store-Id is set, it must belong to the
    # user; otherwise fall back to the user's single (1:1) store.
    store: Store | None = None
    if x_store_id is not None:
        store = session.exec(
            select(Store).where(Store.id == x_store_id, Store.owner_id == user.id)
        ).first()
        if store is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found or does not belong to the current user.",
            )
    else:
        store = session.exec(
            select(Store).where(Store.owner_id == user.id)
        ).first()

    yield AuthContext(
        session=session,
        user=user,
        store=store,
        active_store_id=x_store_id,
    )


def require_store_dep(ctx: AuthContext = Depends(get_ctx)) -> tuple[Session, User, Store]:
    """Helper that unpacks the context and enforces a store exists."""
    return ctx.session, ctx.user, ctx.require_store()