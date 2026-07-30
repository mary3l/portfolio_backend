"""Admin authentication.

The frontend signs in against Supabase directly and sends the resulting access
token as `Authorization: Bearer <token>`. We verify that token with Supabase and
check it belongs to the configured admin account.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase_auth.types import User

from app.core.config import Settings, get_settings
from app.db.supabase import SupabaseClient

# auto_error=False so a missing header produces our own message rather than
# FastAPI's generic "Not authenticated".
bearer_scheme = HTTPBearer(
    auto_error=False,
    scheme_name="SupabaseAccessToken",
    description="Supabase access token from the frontend session.",
)

_INVALID_TOKEN = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired token",
    headers={"WWW-Authenticate": "Bearer"},
)


def require_admin(
    client: SupabaseClient,
    settings: Annotated[Settings, Depends(get_settings)],
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ] = None,
) -> User:
    """Return the signed-in admin, or raise 401/403."""
    if credentials is None or not credentials.credentials.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = client.auth.get_user(credentials.credentials).user
    except Exception as err:  # supabase raises several unrelated error types
        raise _INVALID_TOKEN from err

    if user is None:
        raise _INVALID_TOKEN

    if (user.email or "").lower() != settings.admin_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is not an admin",
        )

    return user


AdminUser = Annotated[User, Depends(require_admin)]
"""Inject the authenticated admin, rejecting everyone else."""
