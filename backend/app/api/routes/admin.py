"""
api/routes/admin.py — Admin-only endpoints
──────────────────────────────────────────
All routes here require is_admin=True on the JWT's user.
The `get_current_admin` dependency handles this check automatically.

Endpoints:
  GET    /admin/stats               → dashboard overview counters
  GET    /admin/users               → all users (with profiles)
  GET    /admin/users/{id}          → single user detail
  PATCH  /admin/users/{id}/toggle   → soft-ban / reactivate
  DELETE /admin/users/{id}          → hard delete
  GET    /admin/food-journal        → all food journal entries
  GET    /admin/workouts            → all workout logs
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_admin
from app.crud.user import (
    get_all_users,
    get_user_by_id,
    toggle_user_active,
    delete_user_by_id,
)
from app.db.models.user import User
from app.db.models.food_journal import FoodJournal
from app.db.models.workout_log import WorkoutLog
from app.schemas.admin import (
    AdminUserResponse,
    AdminStatsResponse,
    AdminFoodJournalEntry,
    AdminWorkoutEntry,
)

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── Stats overview ─────────────────────────────────────────────────────────────

@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),   # auth guard
):
    """
    Return aggregate counts for the admin dashboard overview cards.
    The _admin parameter isn't used — it's here purely to enforce the auth guard.
    """
    return AdminStatsResponse(
        total_users=db.query(User).count(),
        active_users=db.query(User).filter(User.is_active == True).count(),
        admin_users=db.query(User).filter(User.is_admin == True).count(),
        total_journal_entries=db.query(FoodJournal).count(),
        total_workout_logs=db.query(WorkoutLog).count(),
    )


# ── Users ──────────────────────────────────────────────────────────────────────

@router.get("/users", response_model=list[AdminUserResponse])
def list_all_users(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    """Return every user in the system, newest first, with their profile if set."""
    return get_all_users(db)


@router.get("/users/{user_id}", response_model=AdminUserResponse)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    """Return a single user's full record including profile."""
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.patch("/users/{user_id}/toggle", response_model=AdminUserResponse)
def toggle_active(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """
    Flip a user's is_active flag.
    Admins cannot deactivate themselves — that would lock them out.
    """
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own admin account.",
        )
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return toggle_user_active(db, user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """
    Hard-delete a user. Admins cannot delete themselves.
    SQLAlchemy cascade will remove all related profile/journal/workout rows.
    """
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own admin account.",
        )
    deleted = delete_user_by_id(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found.")
    return None  # 204 No Content


# ── Food Journal ───────────────────────────────────────────────────────────────

@router.get("/food-journal", response_model=list[AdminFoodJournalEntry])
def list_all_food_journal(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    """Return all food journal entries across all users, newest first."""
    entries = (
        db.query(FoodJournal)
        .join(User, FoodJournal.user_id == User.id)
        .order_by(FoodJournal.created_at.desc())
        .all()
    )
    return [
        AdminFoodJournalEntry(
            id=e.id,
            user_id=e.user_id,
            user_email=e.user.email,
            date=str(e.date),
            raw_text_entry=e.raw_text_entry,
            estimated_calories=e.estimated_calories,
            estimated_protein=e.estimated_protein,
            created_at=e.created_at,
        )
        for e in entries
    ]


# ── Workouts ───────────────────────────────────────────────────────────────────

@router.get("/workouts", response_model=list[AdminWorkoutEntry])
def list_all_workouts(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    """Return all workout logs across all users, newest first."""
    logs = (
        db.query(WorkoutLog)
        .join(User, WorkoutLog.user_id == User.id)
        .order_by(WorkoutLog.date.desc())
        .all()
    )
    return [
        AdminWorkoutEntry(
            id=log.id,
            user_id=log.user_id,
            user_email=log.user.email,
            exercise=log.exercise,
            sets=log.sets,
            reps=log.reps,
            weight=log.weight,
            date=str(log.date),
        )
        for log in logs
    ]
