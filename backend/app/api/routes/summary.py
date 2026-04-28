import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.crud.profile import get_profile_by_user_id
from app.crud.food_journal import get_entries_by_date
from app.db.models.user import User
from app.schemas.summary import DailySummaryResponse
from app.services.macro_logic import compute_targets, is_profile_complete

router = APIRouter(prefix="/summary", tags=["Summary"])


@router.get("/today", response_model=DailySummaryResponse)
def get_daily_summary(
    date: datetime.date = Query(
        default=None,
        description="Date to summarise (YYYY-MM-DD). Defaults to today.",
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Return a unified daily dashboard summary for the authenticated user.

    A single call gives the frontend everything it needs to render the main
    dashboard: macro targets, consumed totals, remaining budget, and the
    full food log for the day.

    Query param:
        date — optional, defaults to today's date (server timezone).
    """

    # ── Default date to today ──────────────────────────────────────────────────
    target_date = date or datetime.date.today()

    # ── Step A: fetch the user's profile ──────────────────────────────────────
    profile = get_profile_by_user_id(db, user_id=current_user.id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile not found. Please complete your profile before viewing the dashboard.",
        )

    # ── Step B: guard against incomplete profiles, then compute targets ────────
    if not is_profile_complete(
        weight_kg=profile.weight,
        height_cm=profile.height,
        age=profile.age,
        activity_level=profile.activity_level,
        goal=profile.goal,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile is incomplete. Please fill in your weight, height, age, activity level, and goal.",
        )

    targets = compute_targets(
        weight_kg=profile.weight,
        height_cm=profile.height,
        age=profile.age,
        activity_level=profile.activity_level,
        goal=profile.goal,
    )

    # ── Step C: fetch today's food journal entries ─────────────────────────────
    entries = get_entries_by_date(db, user_id=current_user.id, target_date=target_date)

    # ── Step D: sum consumed macros ────────────────────────────────────────────
    # Entries without an AI estimate (None) are treated as 0 — we don't want to
    # crash the whole dashboard just because one entry wasn't estimated yet.
    calories_consumed = sum(e.estimated_calories or 0 for e in entries)
    protein_consumed  = sum(e.estimated_protein  or 0 for e in entries)

    # ── Step E: calculate remaining ────────────────────────────────────────────
    calories_remaining = targets.calories - calories_consumed
    protein_remaining  = targets.protein  - protein_consumed

    # ── Step F: return the unified payload ────────────────────────────────────
    return DailySummaryResponse(
        date=target_date,
        # Targets
        target_calories=targets.calories,
        target_protein=targets.protein,
        target_carbs=targets.carbs,
        target_fat=targets.fat,
        # Consumed
        calories_consumed=calories_consumed,
        protein_consumed=protein_consumed,
        # Remaining
        calories_remaining=calories_remaining,
        protein_remaining=protein_remaining,
        # Log
        log=entries,
    )
