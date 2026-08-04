"""Delivers contact-form enquiries by email via Resend."""

import html
import logging

import httpx

from app.core.config import Settings
from app.core.exceptions import DataAccessError
from app.schemas.contact import ContactRequest

logger = logging.getLogger(__name__)

RESEND_ENDPOINT = "https://api.resend.com/emails"
TIMEOUT_SECONDS = 10.0


def _render_html(enquiry: ContactRequest) -> str:
    """Build the email body.

    Every interpolated value comes from an untrusted form submission, so each one
    is HTML-escaped — otherwise a visitor could inject markup into the mail you
    read.
    """
    rows = [
        ("Name", enquiry.name),
        ("Email", enquiry.email),
        ("Budget", enquiry.budget.label),
        ("Problem", enquiry.problem),
        ("What they want", enquiry.solution),
    ]

    cells = "".join(
        f"""
        <tr>
          <td style="padding:12px 16px;border-bottom:1px solid #e4e4e7;
                     font:600 12px system-ui;text-transform:uppercase;
                     letter-spacing:.08em;color:#71717a;vertical-align:top;
                     white-space:nowrap;">{html.escape(label)}</td>
          <td style="padding:12px 16px;border-bottom:1px solid #e4e4e7;
                     font:14px/1.6 system-ui;color:#18181b;
                     white-space:pre-wrap;">{html.escape(value)}</td>
        </tr>"""
        for label, value in rows
    )

    return f"""<div style="background:#f5f8f6;padding:32px;">
      <div style="max-width:640px;margin:0 auto;background:#fff;
                  border:1px solid #e4e4e7;border-radius:12px;overflow:hidden;">
        <div style="background:#18392b;padding:20px 24px;">
          <p style="margin:0;font:700 16px system-ui;color:#fff;">
            New project enquiry
          </p>
        </div>
        <table style="width:100%;border-collapse:collapse;">{cells}</table>
      </div>
    </div>"""


def _render_text(enquiry: ContactRequest) -> str:
    """Plain-text alternative, for clients that do not render HTML."""
    return (
        f"New project enquiry\n\n"
        f"Name: {enquiry.name}\n"
        f"Email: {enquiry.email}\n"
        f"Budget: {enquiry.budget.label}\n\n"
        f"Problem:\n{enquiry.problem}\n\n"
        f"What they want:\n{enquiry.solution}\n"
    )


def send_enquiry(settings: Settings, enquiry: ContactRequest) -> None:
    """Send one enquiry. Raises `DataAccessError` if Resend rejects it."""
    payload = {
        "from": settings.contact_from_email,
        "to": [settings.contact_recipient],
        # Replying in your mail client goes straight back to the visitor.
        "reply_to": enquiry.email,
        "subject": f"Project enquiry from {enquiry.name}",
        "html": _render_html(enquiry),
        "text": _render_text(enquiry),
    }

    assert settings.resend_api_key is not None  # guarded by contact_enabled
    headers = {
        "Authorization": f"Bearer {settings.resend_api_key.get_secret_value()}",
        "Content-Type": "application/json",
    }

    try:
        response = httpx.post(
            RESEND_ENDPOINT, json=payload, headers=headers, timeout=TIMEOUT_SECONDS
        )
    except httpx.HTTPError as err:
        logger.exception("Could not reach Resend")
        raise DataAccessError(
            "Could not send your message right now. Please email me directly."
        ) from err

    if response.status_code >= 400:
        # Log the provider's reason, but never surface it — it can contain
        # account and key details.
        logger.error(
            "Resend rejected the email (%s): %s", response.status_code, response.text
        )
        raise DataAccessError(
            "Could not send your message right now. Please email me directly."
        )

    logger.info("Enquiry from %s delivered", enquiry.email)
