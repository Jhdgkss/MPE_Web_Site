from __future__ import annotations

import base64
import json
import logging
import os
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Iterable, Optional

logger = logging.getLogger(__name__)


BREVO_API_URL = os.getenv("BREVO_API_URL", "https://api.brevo.com/v3/smtp/email")
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
BREVO_API_TIMEOUT = int(os.getenv("BREVO_API_TIMEOUT", "15"))


@dataclass
class BrevoAttachment:
    filename: str
    content_bytes: bytes
    mime_type: str = "application/octet-stream"

    def as_payload(self) -> dict:
        return {
            "name": self.filename,
            "content": base64.b64encode(self.content_bytes).decode("ascii"),
        }


def send_transactional_email(
    *,
    subject: str,
    text: str,
    to_emails: Iterable[str],
    from_email: str,
    sender_name: Optional[str] = None,
    reply_to: Optional[str] = None,
    attachments: Optional[Iterable[BrevoAttachment]] = None,
) -> None:
    """Send a transactional email via Brevo HTTP API.

    This avoids SMTP (which is often blocked on platform runtimes).
    Requires BREVO_API_KEY environment variable.
    """

    api_key = BREVO_API_KEY
    if not api_key:
        raise RuntimeError("BREVO_API_KEY is not set")

    to_list = [{"email": e} for e in to_emails if e]
    if not to_list:
        raise RuntimeError("No recipients specified")

    sender = {"email": from_email}
    if sender_name:
        sender["name"] = sender_name

    payload: dict = {
        "sender": sender,
        "to": to_list,
        "subject": subject,
        # Keep it simple & robust: send text content.
        # (Brevo accepts htmlContent too if you want later.)
        "textContent": text,
    }

    if reply_to:
        payload["replyTo"] = {"email": reply_to}

    atts = list(attachments or [])
    if atts:
        payload["attachment"] = [a.as_payload() for a in atts]

    body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        BREVO_API_URL,
        data=body,
        headers={
            "api-key": api_key,
            "accept": "application/json",
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=BREVO_API_TIMEOUT) as resp:
            status = getattr(resp, "status", None) or resp.getcode()
            if status < 200 or status >= 300:
                raw = resp.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"Brevo API error HTTP {status}: {raw}")
    except urllib.error.HTTPError as e:
        raw = ""
        try:
            raw = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        raise RuntimeError(f"Brevo API HTTPError {e.code}: {raw or e.reason}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Brevo API connection failed: {e}") from e

