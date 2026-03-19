from datetime import date

from sqlalchemy.orm import Session

from app.db.models.workout_log import WorkoutLog
from app.schemas.workout_log import WorkoutLogCreate, WorkoutLogUpdate


def create_workout_entry(
    db: Session,
    entry_in: WorkoutLogCreate,
    user_id: int,
) -> WorkoutLog:
    """Create a new workout log entry for a user."""
    db_entry = WorkoutLog(
        user_id=user_id,
        **entry_in.model_dump(),
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def get_workouts_by_user(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
) -> list[WorkoutLog]:
    """Return all workout entries for a user, newest first, with pagination."""
    return (
        db.query(WorkoutLog)
        .filter(WorkoutLog.user_id == user_id)
        .order_by(WorkoutLog.date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_workouts_by_date(
    db: Session,
    user_id: int,
    target_date: date,
) -> list[WorkoutLog]:
    """Return all workout entries for a user on a specific date."""
    return (
        db.query(WorkoutLog)
        .filter(
            WorkoutLog.user_id == user_id,
            WorkoutLog.date == target_date,
        )
        .all()
    )


def get_workout_by_id(db: Session, entry_id: int, user_id: int) -> WorkoutLog | None:
    """
    Fetch a single workout entry scoped to the requesting user.

    Same ownership-scoping pattern as food journal — prevents users
    from accessing each other's data via id enumeration.
    """
    return (
        db.query(WorkoutLog)
        .filter(WorkoutLog.id == entry_id, WorkoutLog.user_id == user_id)
        .first()
    )


def update_workout_entry(
    db: Session,
    db_entry: WorkoutLog,
    entry_in: WorkoutLogUpdate,
) -> WorkoutLog:
    """
    Partially update a workout entry.

    Uses exclude_unset=True so only the fields the client explicitly
    sent are changed — same pattern as profile updates.
    """
    update_data = entry_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_entry, field, value)

    db.commit()
    db.refresh(db_entry)
    return db_entry


def delete_workout_entry(db: Session, db_entry: WorkoutLog) -> None:
    """Hard-delete a workout log entry."""
    db.delete(db_entry)
    db.commit()
