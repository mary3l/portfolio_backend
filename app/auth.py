from fastapi import Header, HTTPException

from app.config import ADMIN_EMAIL
from app.database import supabase


def require_admin(authorization: str = Header(default="")):
    """Validate the Supabase access token sent by the frontend as
    `Authorization: Bearer <token>` and make sure it belongs to the admin."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.removeprefix("Bearer ").strip()

    try:
        user = supabase.auth.get_user(token).user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if ADMIN_EMAIL and (user.email or "").lower() != ADMIN_EMAIL.lower():
        raise HTTPException(status_code=403, detail="This account is not an admin")

    return user
