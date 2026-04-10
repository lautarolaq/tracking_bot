from fastapi import Depends, HTTPException, Request

from auth.jwt import decode_token, token_hash
from db import session_exists


async def get_current_user(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido")

    token = auth[7:]
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")

    if not session_exists(token_hash(token)):
        raise HTTPException(status_code=401, detail="Sesión expirada")

    return payload["sub"]
