"""Minimal HS256 JWT signing/verification for demo-mode sessions.

~30 lines of stdlib (hmac + base64 + json) — no PyJWT dependency needed for
the local-only demo path. Real mode verifies tokens against Supabase Auth.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any

_DEMO_TTL_SECONDS = 60 * 60 * 24 * 7  # 7 days


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def sign_demo_token(payload: dict[str, Any], secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    body = {**payload, "iat": now, "exp": now + _DEMO_TTL_SECONDS}
    signing_input = (
        _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
        + "."
        + _b64url_encode(json.dumps(body, separators=(",", ":")).encode())
    )
    signature = hmac.new(secret.encode(), signing_input.encode(), hashlib.sha256).digest()
    return signing_input + "." + _b64url_encode(signature)


def verify_demo_token(token: str, secret: str) -> dict[str, Any] | None:
    try:
        header_b64, body_b64, signature_b64 = token.split(".")
        signing_input = f"{header_b64}.{body_b64}"
        expected = hmac.new(secret.encode(), signing_input.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64url_decode(signature_b64)):
            return None
        body = json.loads(_b64url_decode(body_b64))
        if int(body.get("exp", 0)) < time.time():
            return None
        return body
    except Exception:
        return None
