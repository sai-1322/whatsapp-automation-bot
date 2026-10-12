"""Thin wrapper around the official WhatsApp Business Cloud API."""

import requests

from bot import config


def send_text(to: str, body: str) -> dict:
    """Send a plain text message to `to` (phone number in international format,
    digits only, e.g. "919876543210")."""
    url = (
        f"https://graph.facebook.com/{config.GRAPH_API_VERSION}"
        f"/{config.PHONE_NUMBER_ID}/messages"
    )
    headers = {
        "Authorization": f"Bearer {config.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()
