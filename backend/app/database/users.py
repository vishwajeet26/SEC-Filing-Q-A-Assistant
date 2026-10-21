"""User record provisioning for authenticated users."""

from __future__ import annotations

from sqlalchemy import select

from app.auth.dependencies import CurrentUser
from app.database.models import User
from app.database.session import get_session


def ensure_user(user: CurrentUser) -> None:
    """Insert the authenticated user into the users table if not present."""
    with get_session() as session:
        existing = session.scalar(select(User).where(User.email == user.email))
        if existing is None:
            session.add(User(id=user.id, email=user.email))
            session.commit()
