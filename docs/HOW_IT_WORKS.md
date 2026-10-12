# How this project works (study guide)

Read this, then read the code in the order below. Don't put this project on a resume until you can answer the questions at the bottom without looking.

## The big picture

```
Your phone --> WhatsApp --> Meta servers --POST--> /webhook (this Flask app)
                                                        |
                                              handle_command(text)
                                                        |
Your phone <-- WhatsApp <-- Meta servers <--POST-- whatsapp.send_text(reply)
```

WhatsApp never talks to your phone-number-owner directly. Meta forwards each incoming message to a URL you control (a **webhook**). You reply by calling Meta's **Graph API**.

## Read the code in this order

1. `bot/commands.py` - the "brain". A function that takes text and returns a reply. No internet, no Flask. Start here because it's the easiest to understand and test.
2. `tests/test_commands.py` - shows exactly what each command should do. Break a command on purpose and watch a test fail.
3. `bot/webhook.py` - two helpers:
   - `signature_is_valid`: Meta signs each request with HMAC-SHA256 using your app secret. We recompute and compare, so strangers can't fake messages.
   - `extract_text_messages`: Meta's payload is deeply nested (`entry -> changes -> value -> messages`). This digs out `(sender, text)` pairs and ignores delivery receipts and images.
4. `bot/whatsapp.py` - one HTTP POST to `graph.facebook.com/.../messages` with a Bearer token.
5. `bot/scheduler.py` - `threading.Timer` waits N minutes in a background thread, then sends the reminder.
6. `app.py` - ties it together:
   - `GET /webhook`: one-time handshake. Meta sends a challenge; we echo it back only if the verify token matches.
   - `POST /webhook`: check signature, parse messages, run the command, send the reply, return 200 fast.

## Questions you should be able to answer

1. Why does `GET /webhook` exist, and what happens if the verify token is wrong?
2. Why verify the signature? What attack does it stop?
3. Why does `POST /webhook` always return 200, even if sending the reply fails?
4. Why is `handle_command` kept separate from Flask? (Hint: testing.)
5. What breaks if the server restarts while a reminder is pending? How would you fix it?
6. Why must you use the official Cloud API instead of automating WhatsApp Web?
7. What is the 24-hour window and why does it matter for a reminder bot?

## Make it yours (do these yourself)

- [ ] Add a new command, e.g. `joke`, `weather <city>`, or `todo add/list`, plus a test for it.
- [ ] Persist reminders in SQLite so they survive a restart.
- [ ] Ignore duplicate deliveries by remembering message IDs.
- [ ] Deploy it (Render, Railway or a VPS) so it runs without ngrok.
