import secrets

from fastapi import Header, HTTPException

from app.config import ADMIN_API_KEY


def require_api_key(x_api_key: str = Header(default="")):
    if not secrets.compare_digest(x_api_key, ADMIN_API_KEY):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
