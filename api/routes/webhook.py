import logging
from io import BytesIO

from fastapi import APIRouter, Request, Response
from telegram import Update, Bot

from config import TELEGRAM_BOT_TOKEN, ALLOWED_CHAT_IDS
from llm import transcribe_audio
from handlers.log_event import process_message, format_confirmation
from handlers.summary import generate_summary

router = APIRouter(tags=["telegram"])
logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Simple rate limiter: {chat_id: [timestamps]}
_rate: dict[int, list[float]] = {}
RATE_LIMIT = 30  # max per minute


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


@router.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, bot)

        if not update.message:
            return Response(status_code=200)

        chat_id = update.message.chat_id

        # Validate allowed chat
        if ALLOWED_CHAT_IDS and chat_id not in ALLOWED_CHAT_IDS:
            logger.warning(f"Unauthorized chat_id: {chat_id}")
            return Response(status_code=200)

        # Rate limit
        if not _check_rate(chat_id):
            await bot.send_message(chat_id=chat_id, text="⏳ Demasiados mensajes, esperá un toque")
            return Response(status_code=200)

        # Extract text
        text = None
        if update.message.voice or update.message.audio:
            media = update.message.voice or update.message.audio
            file = await bot.get_file(media.file_id)
            buf = BytesIO()
            await file.download_to_memory(buf)
            audio_bytes = buf.getvalue()
            text = await transcribe_audio(audio_bytes)
            if text:
                # Send transcription preview
                preview = text[:100] + "..." if len(text) > 100 else text
                await bot.send_message(chat_id=chat_id, text=f"🎤 _{preview}_", parse_mode="Markdown")
        else:
            text = update.message.text

        if not text:
            return Response(status_code=200)

        # Process
        events = await process_message(text)

        if not events:
            await bot.send_message(chat_id=chat_id, text="No entendí, probá de nuevo")
            return Response(status_code=200)

        # Check for commands
        for event in events:
            if event.get("category") == "comando":
                cmd_data = event.get("data", {})
                if cmd_data.get("tipo") == "resumen":
                    days = cmd_data.get("dias", 7)
                    summary_text, charts = await generate_summary(days)
                    await bot.send_message(chat_id=chat_id, text=summary_text, parse_mode="Markdown")
                    for chart_bytes in charts:
                        await bot.send_photo(chat_id=chat_id, photo=BytesIO(chart_bytes))
                    return Response(status_code=200)

        # Format confirmations for saved events
        confirmations = []
        for event in events:
            if event.get("category") not in ("unknown", "comando"):
                confirmations.append(format_confirmation(event))

        if confirmations:
            await bot.send_message(chat_id=chat_id, text="\n".join(confirmations))
        else:
            await bot.send_message(chat_id=chat_id, text="No entendí, probá de nuevo")

    except Exception:
        logger.exception("Error processing webhook")

    return Response(status_code=200)
