"""Very small reminder scheduler built on threading.Timer.

Limitation (on purpose, to keep the code easy to read): reminders live in
memory, so they are lost if the server restarts. A good first upgrade for you
is to store them in SQLite and reload them on startup.
"""

import logging
import threading

from bot import whatsapp

log = logging.getLogger(__name__)


def schedule_reminder(to: str, minutes: float, text: str) -> threading.Timer:
    def _fire() -> None:
        try:
            whatsapp.send_text(to, f"Reminder: {text}")
        except Exception:  # never let a failed send crash the timer thread
            log.exception("Failed to send reminder to %s", to)

    timer = threading.Timer(minutes * 60, _fire)
    timer.daemon = True
    timer.start()
    return timer
