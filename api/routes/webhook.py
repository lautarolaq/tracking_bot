import logging
from io import BytesIO

import httpx
from fastapi import APIRouter, Request, Response

from config import TELEGRAM_BOT_TOKEN, ALLOWED_CHAT_IDS
from llm import transcribe_audio
from handlers.log_event import process_message, format_confirmation
from handlers.summary import generate_summary

router = APIRouter(tags=["telegram"])
logger = logging.getLogger(__name__)

TG_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Simple rate limiter: {chat_id: [timestamps]}
_rate: dict[int, list[float]] = {}
RATE_LIMIT = 30


def _check_rate(chat_id: int) -> bool:
    import time
    now = time.time()
    times = _rate.get(chat_id, [])
    times = [t for t in times if now - t < 60]
    if len(times) >= RATE_LIMIT:
        return False
    times.append(now)
    _rate[chat_id] = times
    return True


async def tg_send(chat_id: int, text: str, parse_mode: str = None):
    async with httpx.AsyncClient() as client:
        payload = {"chat_id": chat_id, "text": text}
        if parse_mode:
            payload["parse_mode"] = parse_mode
        await client.post(f"{TG_API}/sendMessage", json=payload)


async def tg_send_photo(chat_id: int, photo_bytes: bytes):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{TG_API}/sendPhoto",
            data={"chat_id": chat_id},
            files={"photo": ("chart.png", photo_bytes, "image/png")},
        )


async def tg_get_file(file_id: str) -> bytes:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{TG_API}/getFile", params={"file_id": file_id})
        file_path = resp.json()["result"]["file_path"]
        file_resp = await client.get(f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}")
        return file_resp.content


@router.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        message = data.get("message")
        if not message:
            return Response(status_code=200)

        chat_id = message["chat"]["id"]

        if ALLOWED_CHAT_IDS and chat_id not in ALLOWED_CHAT_IDS:
            logger.warning(f"Unauthorized chat_id: {chat_id}")
            return Response(status_code=200)

        if not _check_rate(chat_id):
            await tg_send(chat_id, "⏳ Demasiados mensajes, esperá un toque")
            return Response(status_code=200)

        # Extract text
        text = None
        voice = message.get("voice") or message.get("audio")
        if voice:
            file_id = voice["file_id"]
            audio_bytes = await tg_get_file(file_id)
            text = await transcribe_audio(audio_bytes)
            if text:
                preview = text[:100] + "..." if len(text) > 100 else text
                await tg_send(chat_id, f"🎤 _{preview}_", "Markdown")
        else:
            text = message.get("text", "")

        if not text:
            return Response(status_code=200)

        # Process
        events = await process_message(text)

        if not events:
            await tg_send(chat_id, "No entendí, probá de nuevo")
            return Response(status_code=200)

        # Check for commands
        for event in events:
            if event.get("category") == "comando":
                cmd_data = event.get("data", {})
                if cmd_data.get("tipo") == "resumen":
                    days = cmd_data.get("dias", 7)
                    summary_text, charts = await generate_summary(days)
                    await tg_send(chat_id, summary_text, "Markdown")
                    for chart_bytes in charts:
                        await tg_send_photo(chat_id, chart_bytes)
                    return Response(status_code=200)

        # Format confirmations
        confirmations = []
        for event in events:
            if event.get("category") not in ("unknown", "comando"):
                confirmations.append(format_confirmation(event))

        if confirmations:
            await tg_send(chat_id, "\n".join(confirmations))
        else:
            await tg_send(chat_id, "No entendí, probá de nuevo")

    except Exception as e:
        logger.exception("Error processing webhook")

    return Response(status_code=200)
