"""Turns an incoming text message into a reply.

Kept free of Flask and network code so it is trivial to unit test.
"""

from datetime import datetime
from typing import Callable
from zoneinfo import ZoneInfo

from bot import config

MAX_REMINDER_MINUTES = 7 * 24 * 60  # one week

HELP_TEXT = (
    "Available commands:\n"
    "help - show this message\n"
    "ping - check the bot is alive\n"
    "time - current time\n"
    "echo <text> - I repeat what you say\n"
    "remind <minutes> <text> - e.g. remind 10 drink water"
)

# schedule(sender, minutes, text) -> anything
Scheduler = Callable[[str, float, str], object]


def handle_command(text: str, sender: str, schedule: Scheduler) -> str:
    text = (text or "").strip()
    if not text:
        return "Send 'help' to see what I can do."

    command, _, rest = text.partition(" ")
    command = command.lower()
    rest = rest.strip()

    if command in ("help", "hi", "hello", "start"):
        return HELP_TEXT
    if command == "ping":
        return "pong"
    if command == "time":
        now = datetime.now(ZoneInfo(config.BOT_TIMEZONE))
        return now.strftime("It is %I:%M %p on %d %b %Y ") + config.BOT_TIMEZONE
    if command == "echo":
        return rest or "Nothing to echo. Usage: echo <text>"
    if command == "remind":
        return _handle_remind(rest, sender, schedule)

    return "I didn't understand that. Send 'help' to see the commands."


def _handle_remind(args: str, sender: str, schedule: Scheduler) -> str:
    usage = "Usage: remind <minutes> <text>, e.g. remind 10 drink water"
    minutes_str, _, reminder_text = args.partition(" ")
    reminder_text = reminder_text.strip()

    try:
        minutes = float(minutes_str)
    except ValueError:
        return usage
    if not reminder_text:
        return usage
    if not 0 < minutes <= MAX_REMINDER_MINUTES:
        return "Pick a time between 1 minute and 7 days (10080 minutes)."

    schedule(sender, minutes, reminder_text)
    return f"Okay, I'll remind you in {minutes:g} minute(s): {reminder_text}"
