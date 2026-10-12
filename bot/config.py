"""Central place for configuration. Everything comes from environment variables
so secrets never end up in the repository (see .env.example)."""

import os

from dotenv import load_dotenv

load_dotenv()

# Any random string you choose. You paste the same value into the Meta dashboard
# when registering the webhook; Meta sends it back so we know the request is real.
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")

# Permanent access token from Meta (System User token) used to SEND messages.
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")

# The ID of the WhatsApp business phone number (not the phone number itself).
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")

# Your Meta app secret. If set, every incoming webhook is signature-checked.
APP_SECRET = os.getenv("APP_SECRET", "")

GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v21.0")

# Used by the "time" command.
BOT_TIMEZONE = os.getenv("BOT_TIMEZONE", "Asia/Kolkata")
