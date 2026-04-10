import hashlib
from datetime import datetime, timedelta

import jwt as pyjwt

from config import JWT_SECRET, JWT_EXPIRY_DAYS, TZ


def create_token(email: str) -> tuple[str, str]:
    """Returns (token, expires_at_iso)."""
    now = datetime.now(TZ)
    exp = now + timedelta(days=JWT_EXPIRY_DAYS)
    payload = {"sub": email, "exp": exp, "iat": now}
    token = pyjwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token, exp.isoformat()


def decode_token(token: str) -> dict:
    """Returns payload or raises."""
    return pyjwt.decode(token, JWT_SECRET, algorithms=["HS256"])


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
