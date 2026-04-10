import json

from db import get_overview_stats, get_weight_stats, get_nutrition_stats
from llm import generate_summary_text
from charts import generate_weight_chart, generate_nutrition_chart, generate_overview_chart


async def generate_summary(days: int = 7) -> tuple[str, list[bytes]]:
    overview = get_overview_stats(days)
    weight_data = get_weight_stats(days)
    nutrition_data = get_nutrition_stats(days)

    # Build text summary via LLM
    summary_input = json.dumps(overview, ensure_ascii=False, indent=2)
    text = await generate_summary_text(summary_input, days)

    # Generate charts
    charts = []
    overview_chart = generate_overview_chart(overview)
    if overview_chart:
        charts.append(overview_chart)
    weight_chart = generate_weight_chart(weight_data)
    if weight_chart:
        charts.append(weight_chart)
    nutrition_chart = generate_nutrition_chart(nutrition_data)
    if nutrition_chart:
        charts.append(nutrition_chart)

    return text, charts
