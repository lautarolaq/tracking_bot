import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import FRONTEND_URL, DEV_MODE
from db import init_db, cleanup_sessions
from routes.auth import router as auth_router
from routes.api import router as api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    init_db()
    cleanup_sessions()
    logger.info("Ready")
    yield
    logger.info("Shutting down")


app = FastAPI(title="Tracking Personal API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
try:
    from routes.webhook import router as webhook_router
    app.include_router(webhook_router)
    logger.info("Webhook router loaded")
except Exception as e:
    logger.error(f"Failed to load webhook router: {e}")
app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/debug/env")
async def debug_env():
    import os
    return {
        "GROQ_API_KEY": os.environ.get("GROQ_API_KEY", "")[:10] + "..." if os.environ.get("GROQ_API_KEY") else "MISSING",
        "TURSO_DATABASE_URL": os.environ.get("TURSO_DATABASE_URL", "")[:30] + "..." if os.environ.get("TURSO_DATABASE_URL") else "MISSING",
        "TELEGRAM_BOT_TOKEN": "set" if os.environ.get("TELEGRAM_BOT_TOKEN") else "MISSING",
        "ALLOWED_CHAT_IDS": os.environ.get("ALLOWED_CHAT_IDS", "MISSING"),
    }


@app.get("/debug/test-parse")
async def debug_test_parse(text: str = "almorcé milanesa, 700 cal"):
    """Debug endpoint to test LLM parsing."""
    try:
        from handlers.log_event import process_message, format_confirmation
        events = await process_message(text)
        confirmations = [format_confirmation(e) for e in events if e.get("category") not in ("unknown", "comando")]
        return {"events": events, "confirmations": confirmations}
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}
