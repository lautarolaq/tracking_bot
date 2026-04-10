from typing import Optional
from fastapi import APIRouter, Depends, Query

from auth.middleware import get_current_user
from db import (
    get_events,
    get_overview_stats,
    get_weight_stats,
    get_nutrition_stats,
    get_gym_stats,
    get_sleep_stats,
    get_emotion_stats,
    get_work_stats,
    get_correlations,
)

router = APIRouter(prefix="/api", tags=["api"], dependencies=[Depends(get_current_user)])


@router.get("/events")
async def list_events(
    category: Optional[str] = None,
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=100, ge=1, le=1000),
):
    return get_events(category=category, days=days, limit=limit)


@router.get("/stats/overview")
async def stats_overview(days: int = Query(default=30, ge=1, le=365)):
    return get_overview_stats(days)


@router.get("/stats/weight")
async def stats_weight(days: int = Query(default=30, ge=1, le=365)):
    return get_weight_stats(days)


@router.get("/stats/nutrition")
async def stats_nutrition(days: int = Query(default=30, ge=1, le=365)):
    return get_nutrition_stats(days)


@router.get("/stats/gym")
async def stats_gym(days: int = Query(default=30, ge=1, le=365)):
    return get_gym_stats(days)


@router.get("/stats/sleep")
async def stats_sleep(days: int = Query(default=30, ge=1, le=365)):
    return get_sleep_stats(days)


@router.get("/stats/emotions")
async def stats_emotions(days: int = Query(default=30, ge=1, le=365)):
    return get_emotion_stats(days)


@router.get("/stats/work")
async def stats_work(days: int = Query(default=30, ge=1, le=365)):
    return get_work_stats(days)


@router.get("/correlations")
async def correlations(days: int = Query(default=30, ge=1, le=365)):
    return get_correlations(days)
