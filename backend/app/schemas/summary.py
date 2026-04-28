from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from app.schemas.food_journal import FoodJournalResponse


# ── Daily Summary Response ─────────────────────────────────────────────────────
# Returned by GET /api/v1/summary/today.
# The frontend can render the entire dashboard from this single payload.

class DailySummaryResponse(BaseModel):
    # The date this summary covers
    date: date

    # ── Targets (computed from user profile via macro_logic service) ───────────
    target_calories: int
    target_protein: int   # grams
    target_carbs: int     # grams
    target_fat: int       # grams

    # ── Consumed (summed from food journal entries for the day) ────────────────
    calories_consumed: int
    protein_consumed: int  # grams

    # ── Remaining (Target − Consumed) ─────────────────────────────────────────
    # Can be negative if the user has exceeded their targets.
    calories_remaining: int
    protein_remaining: int  # grams

    # ── Log (all food entries for the day, for display in the feed) ───────────
    log: list[FoodJournalResponse]

    model_config = {"from_attributes": True}
