from parser import parse_and_validate
from db import insert_event


async def process_message(text: str, source: str = "telegram") -> list[dict]:
    events = await parse_and_validate(text)

    saved = []
    for event in events:
        cat = event.get("category", "unknown")
        if cat in ("unknown", "comando"):
            saved.append(event)
            continue
        data = event.get("data", {})
        insert_event(cat, data, raw_input=text, source=source)
        saved.append(event)

    return saved


def format_confirmation(event: dict) -> str:
    cat = event.get("category", "")
    data = event.get("data", {})

    if cat == "comida":
        parts = [f"✓ {data.get('kcal', '?')} kcal"]
        macros = []
        if data.get("proteinas"):
            macros.append(f"P:{data['proteinas']}g")
        if data.get("carbos"):
            macros.append(f"C:{data['carbos']}g")
        if data.get("grasas"):
            macros.append(f"G:{data['grasas']}g")
        if macros:
            parts.append(f"({' '.join(macros)})")
        return " ".join(parts)
    elif cat == "gym":
        ex = data.get("ejercicio", "?")
        peso = data.get("peso_kg", "")
        reps = data.get("reps", "")
        sets = data.get("sets", "")
        return f"✓ {ex} {peso}kg {reps}x{sets}" if peso else f"✓ {ex}"
    elif cat == "sueno":
        return f"✓ {data.get('horas', '?')}hs"
    elif cat == "peso":
        return f"✓ {data.get('kg', '?')}kg"
    elif cat == "emocion":
        return "✓ Registrado"
    elif cat == "laburo":
        proy = data.get("proyecto", "")
        return f"✓ {proy}" if proy else "✓ Laburo registrado"
    elif cat == "energia":
        return f"✓ Energía {data.get('nivel', '?')}/10"
    else:
        return "✓ Registrado"
