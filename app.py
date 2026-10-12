"""Flask app exposing the WhatsApp webhook.

Run locally:   python app.py
Production:    gunicorn "app:create_app()"
"""

import logging

from flask import Flask, abort, request

from bot import config, scheduler, whatsapp
from bot.commands import handle_command
from bot.webhook import extract_text_messages, signature_is_valid

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def health():
        return {"status": "ok"}

    @app.get("/webhook")
    def verify():
        """Meta calls this once when you register the webhook URL."""
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge", "")
        if mode == "subscribe" and config.VERIFY_TOKEN and token == config.VERIFY_TOKEN:
            return challenge, 200
        abort(403)

    @app.post("/webhook")
    def receive():
        raw = request.get_data()
        if config.APP_SECRET:
            header = request.headers.get("X-Hub-Signature-256", "")
            if not signature_is_valid(config.APP_SECRET, raw, header):
                abort(403)

        payload = request.get_json(silent=True) or {}
        for sender, text in extract_text_messages(payload):
            reply = handle_command(text, sender, scheduler.schedule_reminder)
            try:
                whatsapp.send_text(sender, reply)
            except Exception:
                log.exception("Failed to reply to %s", sender)

        # Always answer 200 quickly, otherwise Meta keeps retrying the delivery.
        return {"status": "received"}, 200

    return app


if __name__ == "__main__":
    create_app().run(port=5000, debug=True)
