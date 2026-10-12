import hashlib
import hmac
import json

import pytest

from app import create_app
from bot import config


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(config, "VERIFY_TOKEN", "secret-token")
    monkeypatch.setattr(config, "APP_SECRET", "")
    sent = []
    monkeypatch.setattr(
        "bot.whatsapp.send_text", lambda to, body: sent.append((to, body)) or {}
    )
    app = create_app()
    app.sent = sent
    return app.test_client(), sent


def make_payload(text="ping", sender="919800000000", msg_type="text"):
    message = {"from": sender, "type": msg_type}
    if msg_type == "text":
        message["text"] = {"body": text}
    return {"entry": [{"changes": [{"value": {"messages": [message]}}]}]}


def test_health(client):
    c, _ = client
    assert c.get("/").json == {"status": "ok"}


def test_verification_success(client):
    c, _ = client
    r = c.get(
        "/webhook?hub.mode=subscribe&hub.verify_token=secret-token&hub.challenge=1234"
    )
    assert r.status_code == 200
    assert r.get_data(as_text=True) == "1234"


def test_verification_wrong_token(client):
    c, _ = client
    r = c.get("/webhook?hub.mode=subscribe&hub.verify_token=nope&hub.challenge=1")
    assert r.status_code == 403


def test_incoming_message_gets_reply(client):
    c, sent = client
    r = c.post("/webhook", json=make_payload("ping"))
    assert r.status_code == 200
    assert sent == [("919800000000", "pong")]


def test_non_text_and_status_updates_are_ignored(client):
    c, sent = client
    c.post("/webhook", json=make_payload(msg_type="image"))
    c.post("/webhook", json={"entry": [{"changes": [{"value": {"statuses": [{}]}}]}]})
    assert sent == []


def test_signature_enforced_when_secret_set(client, monkeypatch):
    c, sent = client
    monkeypatch.setattr(config, "APP_SECRET", "appsecret")
    body = json.dumps(make_payload("ping")).encode()

    bad = c.post(
        "/webhook",
        data=body,
        content_type="application/json",
        headers={"X-Hub-Signature-256": "sha256=deadbeef"},
    )
    assert bad.status_code == 403
    assert sent == []

    good_sig = hmac.new(b"appsecret", body, hashlib.sha256).hexdigest()
    good = c.post(
        "/webhook",
        data=body,
        content_type="application/json",
        headers={"X-Hub-Signature-256": f"sha256={good_sig}"},
    )
    assert good.status_code == 200
    assert sent == [("919800000000", "pong")]
