import os
from zoneinfo import ZoneInfo

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))
TZ = os.getenv("TZ", "Europe/Rome")
TZINFO = ZoneInfo(TZ)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
AGORHOUR_CRON_SECRET = os.getenv("AGORHOUR_CRON_SECRET", "change-me")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
