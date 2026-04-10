import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


def _setup_style():
    plt.style.use("dark_background")
    plt.rcParams.update({
        "figure.facecolor": "#1e293b",
        "axes.facecolor": "#0f172a",
        "axes.edgecolor": "#334155",
        "axes.labelcolor": "#94a3b8",
        "xtick.color": "#64748b",
        "ytick.color": "#64748b",
        "grid.color": "#1e293b",
        "text.color": "#e2e8f0",
        "font.size": 10,
    })


def _fig_to_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def _parse_dates(date_strings: list[str]) -> list[datetime]:
    return [datetime.fromisoformat(d) for d in date_strings]


def generate_weight_chart(data: list[dict]) -> bytes:
    """data: [{"date": "2024-01-01", "kg": 88.3}, ...]"""
    if not data:
        return b""
    _setup_style()
    fig, ax = plt.subplots(figsize=(10, 4))
    dates = _parse_dates([d["date"] for d in data])
    weights = [d["kg"] for d in data]

    ax.plot(dates, weights, color="#3b82f6", linewidth=2, marker="o", markersize=4)

    # Moving average 7 days
    if len(weights) >= 7:
        ma = []
        for i in range(len(weights)):
            start = max(0, i - 6)
            ma.append(sum(weights[start:i + 1]) / (i - start + 1))
        ax.plot(dates, ma, color="#f59e0b", linewidth=1.5, linestyle="--", alpha=0.7, label="Media 7d")
        ax.legend(loc="upper right")

    ax.set_title("Peso", fontsize=14, fontweight="bold")
    ax.set_ylabel("kg")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()

    return _fig_to_bytes(fig)


def generate_nutrition_chart(data: list[dict], target_kcal: int = 2000) -> bytes:
    """data: [{"date": "2024-01-01", "kcal": 1800}, ...]"""
    if not data:
        return b""
    _setup_style()
    fig, ax = plt.subplots(figsize=(10, 4))
    dates = _parse_dates([d["date"] for d in data])
    kcals = [d["kcal"] for d in data]

    colors = ["#22c55e" if k <= target_kcal else "#ef4444" for k in kcals]
    ax.bar(dates, kcals, color=colors, width=0.8)
    ax.axhline(y=target_kcal, color="#f59e0b", linestyle="--", linewidth=1.5, label=f"Target {target_kcal}")

    ax.set_title("Calorías diarias", fontsize=14, fontweight="bold")
    ax.set_ylabel("kcal")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3, axis="y")
    fig.autofmt_xdate()

    return _fig_to_bytes(fig)


def generate_overview_chart(overview: dict) -> bytes:
    """overview: result from get_overview_stats()"""
    _setup_style()
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle("Resumen", fontsize=16, fontweight="bold")

    # Weight
    ax = axes[0][0]
    peso = overview.get("peso", {})
    ax.text(0.5, 0.5, f'{peso.get("actual", "—")} kg', fontsize=28, fontweight="bold",
            ha="center", va="center", color="#3b82f6", transform=ax.transAxes)
    delta = peso.get("delta", 0)
    color = "#22c55e" if delta <= 0 else "#ef4444"
    sign = "+" if delta > 0 else ""
    ax.text(0.5, 0.2, f'{sign}{delta} kg', fontsize=14, ha="center", va="center",
            color=color, transform=ax.transAxes)
    ax.set_title("Peso")
    ax.axis("off")

    # Nutrition
    ax = axes[0][1]
    nutri = overview.get("nutricion", {})
    ax.text(0.5, 0.5, f'{nutri.get("promedio_kcal", 0)}', fontsize=28, fontweight="bold",
            ha="center", va="center", color="#22c55e", transform=ax.transAxes)
    ax.text(0.5, 0.2, f'kcal/día promedio', fontsize=12, ha="center", va="center",
            color="#94a3b8", transform=ax.transAxes)
    ax.set_title("Nutrición")
    ax.axis("off")

    # Gym
    ax = axes[1][0]
    gym = overview.get("gym", {})
    ax.text(0.5, 0.5, f'{gym.get("dias", 0)}', fontsize=28, fontweight="bold",
            ha="center", va="center", color="#f59e0b", transform=ax.transAxes)
    ax.text(0.5, 0.2, f'días de gym', fontsize=12, ha="center", va="center",
            color="#94a3b8", transform=ax.transAxes)
    ax.set_title("Gym")
    ax.axis("off")

    # Sleep
    ax = axes[1][1]
    sueno = overview.get("sueno", {})
    ax.text(0.5, 0.5, f'{sueno.get("promedio_horas", 0)}h', fontsize=28, fontweight="bold",
            ha="center", va="center", color="#8b5cf6", transform=ax.transAxes)
    ax.text(0.5, 0.2, f'calidad: {sueno.get("promedio_calidad", 0)}/10', fontsize=12,
            ha="center", va="center", color="#94a3b8", transform=ax.transAxes)
    ax.set_title("Sueño")
    ax.axis("off")

    fig.tight_layout()
    return _fig_to_bytes(fig)
