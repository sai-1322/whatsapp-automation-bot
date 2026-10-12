"""Helpers for the incoming webhook: signature check and payload parsing."""

import hashlib
import hmac
from typing import Iterator


def signature_is_valid(app_secret: str, raw_body: bytes, header: str) -> bool:
    """Meta signs every webhook with HMAC-SHA256 using your app secret and sends
    it in the X-Hub-Signature-256 header as 'sha256=<hex>'."""
    if not header or not header.startswith("sha256="):
        return False
    expected = hmac.new(app_secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.removeprefix("sha256="))


def extract_text_messages(payload: dict) -> Iterator[tuple[str, str]]:
    """Yield (sender_number, text) for each plain text message in a webhook
    payload. Status updates (delivered/read) and non-text messages are skipped."""
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for message in value.get("messages", []):
                if message.get("type") != "text":
                    continue
                sender = message.get("from")
                body = message.get("text", {}).get("body", "")
                if sender:
                    yield sender, body
