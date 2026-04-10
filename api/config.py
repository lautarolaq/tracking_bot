import os
from zoneinfo import ZoneInfo

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL", "")
TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN", "")
AUTH_EMAIL = os.environ.get("AUTH_EMAIL", "demo@demo.com")
AUTH_PASSWORD_HASH = os.environ.get("AUTH_PASSWORD_HASH", "")
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-key-change-in-production")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
ALLOWED_CHAT_IDS = [int(x) for x in os.environ.get("ALLOWED_CHAT_IDS", "").split(",") if x.strip()]

DEV_MODE = not TURSO_DATABASE_URL

TZ = ZoneInfo("America/Argentina/Buenos_Aires")
JWT_EXPIRY_DAYS = 30
