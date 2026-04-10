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
if not DEV_MODE:
    from routes.webhook import router as webhook_router
    app.include_router(webhook_router)
app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
