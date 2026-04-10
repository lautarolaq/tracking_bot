import json
import asyncio
from groq import AsyncGroq

from config import GROQ_API_KEY

_groq = AsyncGroq(api_key=GROQ_API_KEY)

PARSE_MODEL = "llama-3.3-70b-versatile"
WHISPER_MODEL = "whisper-large-v3"


async def parse_message(text: str, system_prompt: str) -> list[dict]:
    for attempt in range(3):
        try:
            resp = await _groq.chat.completions.create(
                model=PARSE_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.1,
                max_tokens=1024,
            )
            content = resp.choices[0].message.content.strip()
            # Strip markdown code fences if present
            if content.startswith("```"):
                content = content.split("\n", 1)[1] if "\n" in content else content[3:]
                if content.endswith("```"):
                    content = content[:-3].strip()
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return [parsed]
            return parsed
        except (json.JSONDecodeError, KeyError, IndexError):
            if attempt == 2:
                return [{"category": "unknown", "data": {}, "confidence": 0}]
        except Exception:
            if attempt == 2:
                raise
            await asyncio.sleep(1 * (attempt + 1))
    return [{"category": "unknown", "data": {}, "confidence": 0}]


async def transcribe_audio(file_bytes: bytes, filename: str = "audio.ogg") -> str:
    resp = await _groq.audio.transcriptions.create(
        model=WHISPER_MODEL,
        file=(filename, file_bytes),
        language="es",
    )
    return resp.text


async def generate_summary_text(events_summary: str, days: int) -> str:
    resp = await _groq.chat.completions.create(
        model=PARSE_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Sos un asistente de tracking personal. Generá un resumen conciso y directo "
                    "de los datos del usuario. Sin sermones ni consejos no pedidos. "
                    "Usá español argentino informal. Formato con emojis para Telegram."
                ),
            },
            {
                "role": "user",
                "content": f"Resumen de los últimos {days} días:\n\n{events_summary}",
            },
        ],
        temperature=0.3,
        max_tokens=1024,
    )
    return resp.choices[0].message.content
