"""Liveness and readiness endpoints for uptime checks and deploy probes."""

import logging

from fastapi import APIRouter
from pydantic import BaseModel

from app.db.supabase import SupabaseClient
from app.services.projects import TABLE

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


class Health(BaseModel):
    status: str
    database: str


@router.get("/", summary="Service root")
def root() -> dict[str, str]:
    return {"message": "API is running"}


@router.get("/health", response_model=Health, summary="Health check")
def health(client: SupabaseClient) -> Health:
    """Reports whether the process is up *and* whether Supabase answers.

    Always returns 200 so a probe can distinguish "app down" (no response) from
    "app up, database unreachable" (this payload).
    """
    try:
        client.table(TABLE).select("id").limit(1).execute()
    except Exception:
        # Deliberately broad: a probe must get an answer whatever went wrong
        # (bad credentials, DNS failure, timeout, ...).
        logger.exception("Health check could not reach Supabase")
        return Health(status="degraded", database="unreachable")
    return Health(status="ok", database="ok")
