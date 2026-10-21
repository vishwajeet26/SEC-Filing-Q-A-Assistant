from __future__ import annotations

import hashlib
import uuid

from fastapi import APIRouter, Depends, HTTPException, status


from app.auth.dependencies import CurrentUser, get_current_user
from app.auth.demo_jwt import sign_demo_token
from app.config import settings
from app.database.users import ensure_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
async def me(user: CurrentUser = Depends(get_current_user)) -> dict[str, str]:
    ensure_user(user)
    return {"id": str(user.id), "email": user.email}


def _demo_user_id(email: str) -> uuid.UUID:
    return uuid.UUID(hashlib.sha256(email.strip().lower().encode()).hexdigest()[:32])


def _session_response(email: str) -> dict[str, object]:
    user_id = _demo_user_id(email)
    token = sign_demo_token(
        {"sub": str(user_id), "email": email, "role": "authenticated"},
        settings.demo_jwt_secret,
    )
    return {"accessToken": token, "user": {"id": str(user_id), "email": email}}


def _require_demo_mode() -> None:
    if not settings.is_demo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo auth is disabled; Supabase Auth is configured",
        )


@router.post("/demo/signin")
async def demo_signin(body: dict[str, str]) -> dict[str, object]:
    _require_demo_mode()
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    if not email or len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email and a password of at least 6 characters are required",
        )
    return _session_response(email)


@router.post("/demo/signup")
async def demo_signup(body: dict[str, str]) -> dict[str, object]:
    # Demo sign-up == sign-in: accounts are local and ephemeral.
    return await demo_signin(body)
