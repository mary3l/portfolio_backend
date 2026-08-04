"""Public contact endpoint. Rate-limited and honeypot-protected."""

import logging
import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.config import Settings, get_settings
from app.schemas.contact import ContactRequest, ContactResponse
from app.services import contact as service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contact", tags=["contact"])

# Simple in-process throttle. Enough to stop a script hammering the form; a
# multi-worker deployment would need shared state (Redis) for a hard guarantee.
_RATE_LIMIT = 3
_WINDOW_SECONDS = 600
_recent: dict[str, list[float]] = {}


def _rate_limited(client_ip: str) -> bool:
    now = time.monotonic()
    hits = [t for t in _recent.get(client_ip, []) if now - t < _WINDOW_SECONDS]
    _recent[client_ip] = hits

    if len(hits) >= _RATE_LIMIT:
        return True

    hits.append(now)
    return False


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Send a project enquiry",
    responses={
        429: {"description": "Too many submissions"},
        503: {"description": "Email delivery is not configured"},
    },
)
def send_enquiry(
    payload: ContactRequest,
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
):
    if not settings.contact_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The contact form is not configured yet. Please email me directly.",
        )

    # Honeypot: only a bot fills a field that is hidden from humans. Report
    # success so the bot does not learn to work around it.
    if payload.company:
        logger.info("Discarded honeypot submission from %s", payload.email)
        return ContactResponse(message="Thanks — your message has been sent.")

    client_ip = request.client.host if request.client else "unknown"
    if _rate_limited(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many messages sent. Please try again later.",
        )

    service.send_enquiry(settings, payload)
    return ContactResponse(message="Thanks — your message has been sent.")
