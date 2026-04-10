import json

from db import get_overview_stats, get_weight_stats, get_nutrition_stats
from llm import generate_summary_text


async def generate_summary(days: int = 7) -> tuple[str, list[bytes]]:
    overview = get_overview_stats(days)

    summary_input = json.dumps(overview, ensure_ascii=False, indent=2)
    text = await generate_summary_text(summary_input, days)

    charts = []
    try:
        from charts import generate_weight_chart, generate_nutrition_chart, generate_overview_chart
        weight_data = get_weight_stats(days)
        nutrition_data = get_nutrition_stats(days)
        for fn, data in [(generate_overview_chart, overview), (generate_weight_chart, weight_data), (generate_nutrition_chart, nutrition_data)]:
            chart = fn(data)
            if chart:
                charts.append(chart)
    except ImportError:
        pass

    return text, charts
