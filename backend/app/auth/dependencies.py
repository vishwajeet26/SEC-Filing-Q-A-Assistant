"""FastAPI dependencies for authentication (Supabase JWT or demo token)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.demo_jwt import verify_demo_token
from app.config import settings

_bearer = HTTPBearer(auto_error=False)

# Cached Supabase user lookups share one client.
_http_client: httpx.AsyncClient | None = None


@dataclass(frozen=True, slots=True)
class CurrentUser:
    id: uuid.UUID
    email: str


def _unauthorized(detail: str = "Not authenticated") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_access_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized()

    token = credentials.credentials.strip()
    if not token:
        raise _unauthorized()

    return token


def _demo_user_from_token(token: str) -> CurrentUser:
    body = verify_demo_token(token, settings.demo_jwt_secret)
    if body is None:
        raise _unauthorized("Invalid or expired token")
    try:
        return CurrentUser(id=uuid.UUID(str(body["sub"])), email=str(body["email"]))
    except (KeyError, ValueError) as exc:
        raise _unauthorized("Invalid or expired token") from exc


async def _supabase_user_from_token(token: str) -> CurrentUser:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=10.0)

    try:
        response = await _http_client.get(
            f"{settings.supabase_url.rstrip('/')}/auth/v1/user",
            headers={
                "apikey": settings.supabase_anon_key or "",
                "Authorization": f"Bearer {token}",
            },
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Auth provider unreachable",
        ) from exc

    if response.status_code != 200:
        raise _unauthorized("Invalid or expired token")

    user = response.json()
    user_id = user.get("id")
    email = user.get("email")
    if not user_id or not email:
        raise _unauthorized("Invalid or expired token")

    return CurrentUser(id=uuid.UUID(str(user_id)), email=str(email))


async def get_current_user(
    access_token: str = Depends(get_access_token),
) -> CurrentUser:
    if settings.is_demo:
        return _demo_user_from_token(access_token)
    return await _supabase_user_from_token(access_token)
