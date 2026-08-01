from datetime import date

from sqlalchemy.orm import Session

from app.db.models.food_journal import FoodJournal
from app.schemas.food_journal import FoodJournalCreate, FoodJournalUpdate


def create_food_entry(
    db: Session,
    entry_in: FoodJournalCreate,
    user_id: int,
    estimated_calories: float | None = None,
    estimated_protein: float | None = None,
    is_manual: bool = False,
) -> FoodJournal:
    """
    Create a new food journal entry.

    When is_manual=True the caller supplies the macro values directly and
    the AI estimator has already been skipped at the route level.
    """
    db_entry = FoodJournal(
        user_id=user_id,
        date=entry_in.date,
        raw_text_entry=entry_in.raw_text_entry,
        is_manual=is_manual,
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


def update_food_entry(
    db: Session,
    db_entry: FoodJournal,
    update_in: FoodJournalUpdate,
    estimated_calories: float | None = None,
    estimated_protein: float | None = None,
) -> FoodJournal:
    """
    Apply a partial update to an existing food journal entry.

    Only fields explicitly provided in update_in are changed.
    Callers should pass re-estimated macro values when raw_text_entry changed.
    """
    if update_in.raw_text_entry is not None:
        db_entry.raw_text_entry = update_in.raw_text_entry
        db_entry.estimated_calories = estimated_calories
        db_entry.estimated_protein = estimated_protein
    if update_in.date is not None:
        db_entry.date = update_in.date
    db.commit()
    db.refresh(db_entry)
    return db_entry
