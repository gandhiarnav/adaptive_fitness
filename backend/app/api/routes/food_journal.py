from datetime import date as Date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.crud.food_journal import (
    create_food_entry,
    get_entries_by_user,
    get_entries_by_date,
    get_entry_by_id,
    delete_food_entry,
)
from app.db.models.user import User
from app.schemas.food_journal import FoodJournalCreate, FoodJournalResponse
from app.services.calorie_estimator import estimate_macros  # ← Milestone 5 wired in

router = APIRouter(prefix="/journal", tags=["Food Journal"])


@router.post("/", response_model=FoodJournalResponse, status_code=status.HTTP_201_CREATED)
def log_food(
    entry_in: FoodJournalCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Log a new food entry.

    The raw text is passed through the calorie estimator service before
    being saved. If the estimator returns 0/0 (no known foods found),
    the entry is still saved — just without macro estimates.
    """
    # ── Service layer call ────────────────────────────────────────────────────
    estimate = estimate_macros(entry_in.raw_text_entry)

    return create_food_entry(
        db,
        entry_in=entry_in,
        user_id=current_user.id,
        estimated_calories=estimate.calories or None,  # store None instead of 0
        estimated_protein=estimate.protein or None,
    )


@router.get("/", response_model=list[FoodJournalResponse])
def list_food_entries(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Return all food journal entries for the current user, newest first.

    Supports pagination via skip/limit query params:
      GET /journal?skip=0&limit=20
    """
    return get_entries_by_user(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/by-date", response_model=list[FoodJournalResponse])
def list_food_entries_by_date(
    date: Date = Query(..., description="Format: YYYY-MM-DD"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Return all food entries for the current user on a specific date.

      GET /journal/by-date?date=2026-03-19
    """
    return get_entries_by_date(db, user_id=current_user.id, target_date=date)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food_entry_route(
    entry_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete a specific food journal entry.

    The ownership check inside get_entry_by_id ensures users can only
    delete their own entries.
    """
    entry = get_entry_by_id(db, entry_id=entry_id, user_id=current_user.id)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found.",
        )
    delete_food_entry(db, db_entry=entry)
