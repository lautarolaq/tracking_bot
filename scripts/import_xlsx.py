"""Import comidas xlsx v2 into tracking-bot SQLite dev DB."""
import re
import json
import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "/tmp/tracking-dev.db"
XLSX_PATH = "/Users/lautaro/Downloads/registro_de_comidas_v2.xlsx"


def parse_date(val, prev_date=None):
    if isinstance(val, datetime):
        if val.day <= 12 and val.month <= 12 and prev_date:
            swapped = val.replace(month=val.day, day=val.month)
            diff_orig = abs((val - prev_date).days)
            diff_swap = abs((swapped - prev_date).days)
            if diff_swap < diff_orig:
                return swapped
        return val
    if isinstance(val, str):
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(val, fmt)
            except ValueError:
                continue
    return None


def extract_peso(notas):
    if not isinstance(notas, str):
        return None
    m = re.search(r'[Pp]eso[:\s]*(\d+[\.,]?\d*)\s*kg', notas)
    return float(m.group(1).replace(',', '.')) if m else None


def classify_exercise(ex):
    if not isinstance(ex, str) or ex.strip() in ('-', 'Ninguno', '', 'nan'):
        return []
    ex_lower = ex.lower()
    result = []
    if 'gym' in ex_lower:
        result.append(('gym', None))
    km = re.search(r'(\d+[\.,]?\d*)\s*km', ex_lower)
    if 'caminata' in ex_lower or 'caminar' in ex_lower:
        result.append(('caminata', float(km.group(1).replace(',', '.')) if km else None))
    if not result and ex.strip() not in ('-', 'Ninguno'):
        result.append(('otro', ex.strip()))
    return result


def build_meal_description(row):
    meals = []
    for col in ['Desayuno', 'Almuerzo', 'Merienda', 'Cena']:
        val = row.get(col)
        if isinstance(val, str) and val.strip() not in ('-', '', 'No cenó', 'nan'):
            meals.append(f"{col}: {val.strip()}")
    return "; ".join(meals) if meals else None


def main():
    df = pd.read_excel(XLSX_PATH)
    conn = sqlite3.connect(DB_PATH)

    conn.execute("DELETE FROM events WHERE source = 'xlsx_import'")
    conn.execute("DELETE FROM events WHERE source = 'demo'")
    conn.commit()

    inserted = {"comida": 0, "gym": 0, "peso": 0, "emocion": 0}
    prev_date = None

    for _, row in df.iterrows():
        fecha = parse_date(row['Fecha'], prev_date)
        if not fecha:
            print(f"Skipping bad date: {row['Fecha']}")
            continue
        prev_date = fecha
        ts = fecha.replace(hour=12).isoformat() + "-03:00"

        # 1. Comida with full nutrition data
        desc = build_meal_description(row)
        if desc:
            kcal = int(row.get('Calorías (kcal)', 0)) if pd.notna(row.get('Calorías (kcal)')) else 0
            prot = int(row.get('Proteína (g)', 0)) if pd.notna(row.get('Proteína (g)')) else 0
            carbs = int(row.get('Carbs (g)', 0)) if pd.notna(row.get('Carbs (g)')) else 0
            grasas = int(row.get('Grasa (g)', 0)) if pd.notna(row.get('Grasa (g)')) else 0

            data = {"descripcion": desc, "kcal": kcal, "proteinas": prot, "carbos": carbs, "grasas": grasas}
            conn.execute(
                "INSERT INTO events (timestamp, category, data, raw_input, source) VALUES (?, ?, ?, ?, ?)",
                [ts, "comida", json.dumps(data, ensure_ascii=False), desc, "xlsx_import"]
            )
            inserted["comida"] += 1

        # 2. Gym/exercise
        exercises = classify_exercise(row.get('Ejercicio'))
        for ex_type, ex_val in exercises:
            ex_ts = fecha.replace(hour=17).isoformat() + "-03:00"
            if ex_type == 'gym':
                conn.execute(
                    "INSERT INTO events (timestamp, category, data, raw_input, source) VALUES (?, ?, ?, ?, ?)",
                    [ex_ts, "gym", json.dumps({"ejercicio": "sesión gym", "sensacion": 7}),
                     str(row.get('Ejercicio', '')), "xlsx_import"]
                )
            elif ex_type == 'caminata':
                data = {"ejercicio": "caminata"}
                if ex_val:
                    data["distancia_km"] = ex_val
                conn.execute(
                    "INSERT INTO events (timestamp, category, data, raw_input, source) VALUES (?, ?, ?, ?, ?)",
                    [ex_ts, "gym", json.dumps(data), str(row.get('Ejercicio', '')), "xlsx_import"]
                )
            else:
                conn.execute(
                    "INSERT INTO events (timestamp, category, data, raw_input, source) VALUES (?, ?, ?, ?, ?)",
                    [ex_ts, "gym", json.dumps({"ejercicio": ex_val or "ejercicio"}),
                     str(row.get('Ejercicio', '')), "xlsx_import"]
                )
            inserted["gym"] += 1

        # 3. Peso from notes
        notas_str = str(row.get('Notas y Peso', '')) if pd.notna(row.get('Notas y Peso')) else ''
        peso = extract_peso(notas_str)
        if peso:
            peso_ts = fecha.replace(hour=8).isoformat() + "-03:00"
            conn.execute(
                "INSERT INTO events (timestamp, category, data, raw_input, source) VALUES (?, ?, ?, ?, ?)",
                [peso_ts, "peso", json.dumps({"kg": peso}), f"{peso}kg", "xlsx_import"]
            )
            inserted["peso"] += 1

        # 4. Estado emocional
        emo = row.get('Estado emocional', '')
        if isinstance(emo, str) and emo.strip() not in ('-', '', 'nan'):
            conn.execute(
                "INSERT INTO events (timestamp, category, data, raw_input, source) VALUES (?, ?, ?, ?, ?)",
                [ts, "emocion",
                 json.dumps({"situacion": emo.strip(), "intensidad": 5}, ensure_ascii=False),
                 emo.strip(), "xlsx_import"]
            )
            inserted["emocion"] += 1

    conn.commit()

    # Verify dates
    print("Date sequence check:")
    rows = conn.execute("SELECT DISTINCT substr(timestamp,1,10) as d FROM events ORDER BY d").fetchall()
    for r in rows:
        print(f"  {r[0]}")

    print(f"\nImport complete!")
    for k, v in inserted.items():
        print(f"  {k}: {v}")
    total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    print(f"  Total events: {total}")
    conn.close()


if __name__ == "__main__":
    main()
