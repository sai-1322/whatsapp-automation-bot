# WhatsApp Automation Bot

A small Python bot that replies to WhatsApp messages and sends scheduled reminders, built on the **official WhatsApp Business Cloud API** (no unofficial libraries, no risk of getting your number banned).

## What it does

| You send | Bot replies |
|---|---|
| `help` | List of commands |
| `ping` | `pong` |
| `time` | Current time in your timezone |
| `echo hello` | `hello` |
| `remind 10 drink water` | Confirms, then messages you "Reminder: drink water" 10 minutes later |

## Tech

- Python 3.10+, Flask (webhook server)
- `requests` (calls the WhatsApp Cloud API)
- `pytest` (17 tests)

## Project layout

```
app.py              Flask app: webhook verification + receiving messages
bot/commands.py     Pure logic: text in -> reply out (easy to test)
bot/webhook.py      Signature check + payload parsing
bot/whatsapp.py     Sends messages through the Cloud API
bot/scheduler.py    In-memory reminders
bot/config.py       Environment-variable config
tests/              Unit + webhook tests
docs/HOW_IT_WORKS.md  Step-by-step walkthrough of the code
```

## Run it locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then fill in your values
python -m pytest            # should be all green
python app.py               # starts on http://localhost:5000
```

## Connect it to WhatsApp

1. Create an app at [developers.facebook.com](https://developers.facebook.com) and add the **WhatsApp** product. Meta gives you a free test number.
2. Copy the **temporary access token** and **Phone number ID** into `.env`.
3. Expose your local server with a tunnel, e.g. `ngrok http 5000`.
4. In the Meta dashboard, set the webhook callback URL to `https://<your-tunnel>/webhook` and the verify token to the same `VERIFY_TOKEN` you put in `.env`. Subscribe to the `messages` field.
5. Add your own phone as a test recipient, message the test number, and send `help`.

## Known limitations / ideas to extend

- Reminders are stored in memory and vanish on restart. Persist them in SQLite.
- Only handles text messages. Add image/document handling.
- No duplicate-delivery protection (Meta can retry). Track processed message IDs.
- Free-form replies only work within 24 hours of the user's last message; outside that window WhatsApp requires approved message templates.

## Credits

Initial version built with AI assistance (Claude) and then studied, run and extended by the repository owner.
