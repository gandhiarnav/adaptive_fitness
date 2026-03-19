from datetime import date as Date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.crud.workout_log import (
    create_workout_entry,
    get_workouts_by_user,
    get_workouts_by_date,
    get_workout_by_id,
    update_workout_entry,
    delete_workout_entry,
)
from app.db.models.user import User
from app.schemas.workout_log import WorkoutLogCreate, WorkoutLogUpdate, WorkoutLogResponse

router = APIRouter(prefix="/workout", tags=["Workout"])


@router.post("/", response_model=WorkoutLogResponse, status_code=status.HTTP_201_CREATED)
def log_workout(
    entry_in: WorkoutLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Log a new workout entry for the current user."""
    return create_workout_entry(db, entry_in=entry_in, user_id=current_user.id)


@router.get("/", response_model=list[WorkoutLogResponse])
def list_workouts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Return all workout entries for the current user, newest first.

    Supports pagination via skip/limit query params:
      GET /workout?skip=0&limit=20
    """
    return get_workouts_by_user(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/by-date", response_model=list[WorkoutLogResponse])
def list_workouts_by_date(
    date: Date = Query(..., description="Format: YYYY-MM-DD"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Return all workout entries for the current user on a specific date.

      GET /workout/by-date?date=2026-03-19
    """
    return get_workouts_by_date(db, user_id=current_user.id, target_date=date)


@router.patch("/{entry_id}", response_model=WorkoutLogResponse)
def update_workout(
    entry_id: int,
    entry_in: WorkoutLogUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Partially update a workout entry.

    Only fields included in the request body are changed.
    Returns 404 if the entry doesn't exist or belongs to another user.
    """
    entry = get_workout_by_id(db, entry_id=entry_id, user_id=current_user.id)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout entry not found.",
        )
    return update_workout_entry(db, db_entry=entry, entry_in=entry_in)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(
    entry_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete a specific workout entry.

    Ownership-scoped — users can only delete their own entries.
    """
    entry = get_workout_by_id(db, entry_id=entry_id, user_id=current_user.id)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout entry not found.",
        )
    delete_workout_entry(db, db_entry=entry)
