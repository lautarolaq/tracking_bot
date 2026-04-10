from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from config import AUTH_EMAIL, AUTH_PASSWORD_HASH, DEV_MODE
from auth.password import verify_password
from auth.jwt import create_token, token_hash
from auth.middleware import get_current_user
from db import save_session, delete_session

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest):
    if DEV_MODE:
        # In dev mode accept any credentials
        pass
    elif body.email != AUTH_EMAIL or not verify_password(body.password, AUTH_PASSWORD_HASH):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token, expires_at = create_token(body.email)
    save_session(token_hash(token), expires_at)
    return {"token": token}


@router.get("/me")
async def me(email: str = Depends(get_current_user)):
    return {"email": email}


@router.post("/logout")
async def logout(request: Request, email: str = Depends(get_current_user)):
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        delete_session(token_hash(auth[7:]))
    return {"ok": True}
