import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
import random

from config import TURSO_DATABASE_URL, TURSO_AUTH_TOKEN, TZ, DEV_MODE

_conn = None


class _Result:
    def __init__(self, rows):
        self.rows = rows


class _LocalClient:
    def __init__(self, path=":memory:"):
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA journal_mode=WAL")

    def execute(self, sql, params=None):
        cur = self.conn.execute(sql, params or [])
        self.conn.commit()
        return _Result(cur.fetchall())


class _TursoClient:
    def __init__(self, url, auth_token):
        import libsql_experimental as libsql
        self.conn = libsql.connect("tracking.db", sync_url=url, auth_token=auth_token)
        self.conn.sync()

    def execute(self, sql, params=None):
        cur = self.conn.execute(sql, params or [])
        self.conn.commit()
        return _Result(cur.fetchall())


def _get_client():
    global _conn
    if _conn is None:
        if DEV_MODE:
            _conn = _LocalClient("/tmp/tracking-dev.db")
        else:
            _conn = _TursoClient(TURSO_DATABASE_URL, TURSO_AUTH_TOKEN)
    return _conn


def init_db():
    c = _get_client()
    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            category TEXT NOT NULL,
            data TEXT NOT NULL,
            raw_input TEXT,
            source TEXT DEFAULT 'telegram'
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_events_category ON events(category)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)")
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token_hash TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL
        )
    """)
    if DEV_MODE:
        _seed_demo_data()


def _seed_demo_data():
    c = _get_client()
    rs = c.execute("SELECT COUNT(*) FROM events")
    if rs.rows[0][0] > 0:
        return

    now = datetime.now(TZ)
    events = []

    for i in range(30):
        day = now - timedelta(days=29 - i)
        ds = day.isoformat()
        date_str = day.strftime("%Y-%m-%d")

        # Weight: trending down from 90 to 87
        kg = round(90 - (i * 0.1) + random.uniform(-0.3, 0.3), 1)
        events.append((ds, "peso", json.dumps({"kg": kg}), f"{kg}", "demo"))

        # Nutrition: 2-3 meals per day
        for meal_i in range(random.randint(2, 3)):
            meals = [
                ("milanesa con ensalada", 700, 40, 50, 30),
                ("ensalada de pollo", 450, 35, 20, 15),
                ("pasta con salsa", 600, 20, 80, 15),
                ("tostadas con palta", 350, 10, 30, 20),
                ("hamburguesa", 800, 35, 60, 40),
                ("arroz con pollo", 550, 30, 60, 12),
                ("yogur con granola", 300, 15, 40, 8),
                ("empanadas x3", 650, 25, 45, 30),
            ]
            desc, kcal, prot, carb, fat = random.choice(meals)
            kcal += random.randint(-50, 50)
            meal_time = day.replace(hour=random.choice([8, 13, 20]), minute=random.randint(0, 59))
            events.append((meal_time.isoformat(), "comida",
                           json.dumps({"kcal": kcal, "descripcion": desc, "proteinas": prot, "carbos": carb, "grasas": fat}),
                           f"{desc}, {kcal} cal", "demo"))

        # Gym: 4 days per week
        if day.weekday() in (0, 2, 3, 5):
            exercises = [
                ("press banca", 80, 8, 3),
                ("sentadilla", 100, 6, 4),
                ("peso muerto", 120, 5, 3),
                ("remo con barra", 70, 8, 3),
                ("press militar", 50, 8, 3),
                ("curl biceps", 30, 10, 3),
                ("fondos", 0, 12, 3),
            ]
            for _ in range(random.randint(3, 5)):
                ex, peso, reps, sets = random.choice(exercises)
                peso_var = peso + random.uniform(-5, 5)
                sensacion = random.randint(5, 9)
                gym_time = day.replace(hour=random.choice([7, 17, 18]), minute=random.randint(0, 59))
                events.append((gym_time.isoformat(), "gym",
                               json.dumps({"ejercicio": ex, "peso_kg": round(peso_var, 1), "reps": reps, "sets": sets, "sensacion": sensacion}),
                               f"{ex} {peso_var}x{reps}x{sets}", "demo"))

        # Sleep
        horas = round(random.uniform(5, 8.5), 1)
        calidad = random.randint(3, 9)
        events.append((ds, "sueno", json.dumps({"horas": horas, "calidad": calidad}), f"dormí {horas}hs", "demo"))

        # Emotions: some days
        if random.random() < 0.3:
            situaciones = [
                ("discusión con cliente", 7, "activacion"),
                ("ansiedad por deadline", 6, "panza"),
                ("conflicto familiar", 8, "activacion"),
                ("frustración con bug", 5, ""),
                ("pelea con el banco", 9, "activacion"),
            ]
            sit, intens, senal = random.choice(situaciones)
            events.append((ds, "emocion",
                           json.dumps({"situacion": sit, "intensidad": intens, "senal_fisica": senal}),
                           sit, "demo"))

        # Work: some days
        if random.random() < 0.4:
            proyectos = [
                ("CreditIQ", 7, "deadline esta semana"),
                ("MejorTasa", 5, "review de código"),
                ("PropHunter", 6, "deploy a producción"),
                ("CreditIQ", 8, "bug crítico en prod"),
                ("MejorTasa", 4, "reunión de planning"),
            ]
            proy, estres, ctx = random.choice(proyectos)
            events.append((ds, "laburo",
                           json.dumps({"proyecto": proy, "estres": estres, "contexto": ctx}),
                           f"{proy}: {ctx}", "demo"))

    for ts, cat, data, raw, source in events:
        c.execute(
            "INSERT INTO events (timestamp, category, data, raw_input, source) VALUES (?, ?, ?, ?, ?)",
            [ts, cat, data, raw, source],
        )


def now_ar():
    return datetime.now(TZ).isoformat()


def insert_event(category: str, data: dict, raw_input: Optional[str] = None, source: str = "telegram"):
    c = _get_client()
    c.execute(
        "INSERT INTO events (timestamp, category, data, raw_input, source) VALUES (?, ?, ?, ?, ?)",
        [now_ar(), category, json.dumps(data, ensure_ascii=False), raw_input, source],
    )


def get_events(category: Optional[str] = None, days: int = 30, limit: int = 100):
    c = _get_client()
    since = (datetime.now(TZ) - timedelta(days=days)).isoformat()
    if category:
        rs = c.execute(
            "SELECT id, timestamp, category, data, raw_input FROM events WHERE category = ? AND timestamp >= ? ORDER BY timestamp DESC LIMIT ?",
            [category, since, limit],
        )
    else:
        rs = c.execute(
            "SELECT id, timestamp, category, data, raw_input FROM events WHERE timestamp >= ? ORDER BY timestamp DESC LIMIT ?",
            [since, limit],
        )
    return [
        {"id": r[0], "timestamp": r[1], "category": r[2], "data": json.loads(r[3]), "raw_input": r[4]}
        for r in rs.rows
    ]


def get_events_by_category(category: str, days: int = 30):
    return get_events(category=category, days=days, limit=10000)


# --- Stats queries ---

def get_weight_stats(days: int = 30):
    rows = get_events_by_category("peso", days)
    return [{"date": r["timestamp"][:10], "kg": r["data"].get("kg")} for r in reversed(rows)]


def get_nutrition_stats(days: int = 30):
    rows = get_events_by_category("comida", days)
    by_date: dict[str, dict] = {}
    for r in rows:
        d = r["timestamp"][:10]
        if d not in by_date:
            by_date[d] = {"date": d, "kcal": 0, "proteinas": 0, "carbos": 0, "grasas": 0}
        by_date[d]["kcal"] += r["data"].get("kcal", 0)
        by_date[d]["proteinas"] += r["data"].get("proteinas", 0)
        by_date[d]["carbos"] += r["data"].get("carbos", 0)
        by_date[d]["grasas"] += r["data"].get("grasas", 0)
    return sorted(by_date.values(), key=lambda x: x["date"])


def get_gym_stats(days: int = 30):
    rows = get_events_by_category("gym", days)
    by_day: dict[str, dict] = {}
    by_exercise: dict[str, dict] = {}
    for r in rows:
        d = r["timestamp"][:10]
        ex = r["data"].get("ejercicio", "desconocido")
        peso = r["data"].get("peso_kg", 0)
        reps = r["data"].get("reps", 0)
        sets = r["data"].get("sets", 0)
        vol = peso * reps * sets

        if d not in by_day:
            by_day[d] = {"date": d, "ejercicios": 0, "volumen_total": 0}
        by_day[d]["ejercicios"] += 1
        by_day[d]["volumen_total"] += vol

        if ex not in by_exercise:
            by_exercise[ex] = {"ejercicio": ex, "max_peso": 0, "total_sets": 0}
        by_exercise[ex]["max_peso"] = max(by_exercise[ex]["max_peso"], peso)
        by_exercise[ex]["total_sets"] += sets

    return {
        "por_dia": sorted(by_day.values(), key=lambda x: x["date"]),
        "por_ejercicio": list(by_exercise.values()),
    }


def get_sleep_stats(days: int = 30):
    rows = get_events_by_category("sueno", days)
    return [
        {"date": r["timestamp"][:10], "horas": r["data"].get("horas", 0), "calidad": r["data"].get("calidad", 0)}
        for r in reversed(rows)
    ]


def get_emotion_stats(days: int = 30):
    rows = get_events_by_category("emocion", days)
    return [
        {
            "timestamp": r["timestamp"],
            "situacion": r["data"].get("situacion", ""),
            "intensidad": r["data"].get("intensidad", 0),
            "senal_fisica": r["data"].get("senal_fisica", ""),
        }
        for r in rows
    ]


def get_work_stats(days: int = 30):
    rows = get_events_by_category("laburo", days)
    return [
        {
            "timestamp": r["timestamp"],
            "proyecto": r["data"].get("proyecto", ""),
            "estres": r["data"].get("estres", 0),
            "contexto": r["data"].get("contexto", ""),
        }
        for r in rows
    ]


def get_overview_stats(days: int = 30):
    weight = get_weight_stats(days)
    nutrition = get_nutrition_stats(days)
    gym = get_gym_stats(days)
    sleep = get_sleep_stats(days)
    emotions = get_emotion_stats(days)

    peso_actual = weight[-1]["kg"] if weight else None
    peso_anterior = weight[0]["kg"] if len(weight) > 1 else peso_actual
    peso_delta = round(peso_actual - peso_anterior, 1) if peso_actual and peso_anterior else 0

    avg_kcal = round(sum(d["kcal"] for d in nutrition) / len(nutrition)) if nutrition else 0
    dias_deficit = sum(1 for d in nutrition if d["kcal"] < 2000)

    dias_gym = len(gym["por_dia"])
    vol_total = sum(d["volumen_total"] for d in gym["por_dia"])

    avg_horas = round(sum(d["horas"] for d in sleep) / len(sleep), 1) if sleep else 0
    avg_calidad = round(sum(d["calidad"] for d in sleep) / len(sleep), 1) if sleep else 0

    total_emociones = len(emotions)
    avg_intensidad = round(sum(e["intensidad"] for e in emotions) / len(emotions), 1) if emotions else 0

    return {
        "peso": {"actual": peso_actual, "delta": peso_delta},
        "nutricion": {"promedio_kcal": avg_kcal, "dias_en_deficit": dias_deficit},
        "gym": {"dias": dias_gym, "volumen_total": vol_total},
        "sueno": {"promedio_horas": avg_horas, "promedio_calidad": avg_calidad},
        "emociones": {"total_activaciones": total_emociones, "intensidad_promedio": avg_intensidad},
    }


def get_correlations(days: int = 30):
    sleep = get_sleep_stats(days)
    gym = get_gym_stats(days)
    nutrition = get_nutrition_stats(days)
    work = get_work_stats(days)

    sleep_by_date = {s["date"]: s for s in sleep}
    gym_dates = {d["date"] for d in gym["por_dia"]}
    nutrition_by_date = {n["date"]: n for n in nutrition}

    gym_sleep = [sleep_by_date[d]["calidad"] for d in gym_dates if d in sleep_by_date]
    rest_sleep = [s["calidad"] for d, s in sleep_by_date.items() if d not in gym_dates]
    avg_gym_sleep = round(sum(gym_sleep) / len(gym_sleep), 1) if gym_sleep else 0
    avg_rest_sleep = round(sum(rest_sleep) / len(rest_sleep), 1) if rest_sleep else 0

    weekday_kcal = []
    weekend_kcal = []
    for n in nutrition:
        try:
            dt = datetime.fromisoformat(n["date"])
            if dt.weekday() < 5:
                weekday_kcal.append(n["kcal"])
            else:
                weekend_kcal.append(n["kcal"])
        except ValueError:
            pass

    avg_weekday = round(sum(weekday_kcal) / len(weekday_kcal)) if weekday_kcal else 0
    avg_weekend = round(sum(weekend_kcal) / len(weekend_kcal)) if weekend_kcal else 0

    work_by_date: dict[str, float] = {}
    for w in work:
        d = w["timestamp"][:10]
        work_by_date[d] = max(work_by_date.get(d, 0), w["estres"])

    stress_high_kcal = []
    stress_low_kcal = []
    for d, n in nutrition_by_date.items():
        stress = work_by_date.get(d, 0)
        if stress >= 7:
            stress_high_kcal.append(n["kcal"])
        elif stress > 0:
            stress_low_kcal.append(n["kcal"])

    avg_stress_high = round(sum(stress_high_kcal) / len(stress_high_kcal)) if stress_high_kcal else 0
    avg_stress_low = round(sum(stress_low_kcal) / len(stress_low_kcal)) if stress_low_kcal else 0

    return {
        "sueno_vs_gym": {
            "calidad_dias_gym": avg_gym_sleep,
            "calidad_dias_descanso": avg_rest_sleep,
            "data_points": len(gym_sleep) + len(rest_sleep),
        },
        "estres_vs_nutricion": {
            "kcal_estres_alto": avg_stress_high,
            "kcal_estres_bajo": avg_stress_low,
            "data_points": len(stress_high_kcal) + len(stress_low_kcal),
        },
        "finde_vs_semana": {
            "promedio_semana": avg_weekday,
            "promedio_finde": avg_weekend,
        },
    }


# --- Sessions ---

def save_session(token_hash: str, expires_at: str):
    c = _get_client()
    c.execute(
        "INSERT OR REPLACE INTO sessions (token_hash, created_at, expires_at) VALUES (?, ?, ?)",
        [token_hash, now_ar(), expires_at],
    )


def session_exists(token_hash: str) -> bool:
    c = _get_client()
    rs = c.execute("SELECT 1 FROM sessions WHERE token_hash = ?", [token_hash])
    return len(rs.rows) > 0


def delete_session(token_hash: str):
    c = _get_client()
    c.execute("DELETE FROM sessions WHERE token_hash = ?", [token_hash])


def cleanup_sessions():
    c = _get_client()
    c.execute("DELETE FROM sessions WHERE expires_at < ?", [now_ar()])
