from datetime import date

from sqlalchemy.orm import Session

from app.db.models.food_journal import FoodJournal
from app.schemas.food_journal import FoodJournalCreate


def create_food_entry(
    db: Session,
    entry_in: FoodJournalCreate,
    user_id: int,
    estimated_calories: int | None = None,
    estimated_protein: int | None = None,
) -> FoodJournal:
    """
    Create a new food journal entry.

    estimated_calories and estimated_protein are optional here because
    in Milestone 5 the calorie_estimator service will compute them and
    pass them in. For now, entries can be saved without estimates.
    """
    db_entry = FoodJournal(
        user_id=user_id,
        date=entry_in.date,
        raw_text_entry=entry_in.raw_text_entry,
        estimated_calories=estimated_calories,
        estimated_protein=estimated_protein,
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def get_entries_by_user(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
) -> list[FoodJournal]:
    """
    Return all journal entries for a user, newest first.

    skip/limit enable pagination so we never accidentally return thousands
    of rows to the client in one shot.
    """
    return (
        db.query(FoodJournal)
        .filter(FoodJournal.user_id == user_id)
        .order_by(FoodJournal.date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_entries_by_date(
    db: Session,
    user_id: int,
    target_date: date,
) -> list[FoodJournal]:
    """Return all food entries for a user on a specific date."""
    return (
        db.query(FoodJournal)
        .filter(
            FoodJournal.user_id == user_id,
            FoodJournal.date == target_date,
        )
        .all()
    )


def get_entry_by_id(db: Session, entry_id: int, user_id: int) -> FoodJournal | None:
    """
    Fetch a single entry by its id, scoped to the requesting user.

    Scoping by user_id means user A can never read user B's entries
    even if they guess the entry's integer id.
    """
    return (
        db.query(FoodJournal)
        .filter(FoodJournal.id == entry_id, FoodJournal.user_id == user_id)
        .first()
    )


def delete_food_entry(db: Session, db_entry: FoodJournal) -> None:
    """Hard-delete a food journal entry."""
    db.delete(db_entry)
    db.commit()
