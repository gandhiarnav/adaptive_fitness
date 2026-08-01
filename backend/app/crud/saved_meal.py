from sqlalchemy.orm import Session

from app.db.models.saved_meal import SavedMeal
from app.schemas.saved_meal import SavedMealCreate


def create_saved_meal(
    db: Session,
    meal_in: SavedMealCreate,
    user_id: int,
) -> SavedMeal:
    """Persist a new saved meal for a user."""
    db_meal = SavedMeal(
        user_id=user_id,
        name=meal_in.name,
        calories=meal_in.calories,
        protein=meal_in.protein,
    )
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal


def get_saved_meals(db: Session, user_id: int) -> list[SavedMeal]:
    """Return all saved meals for a user, newest first."""
    return (
        db.query(SavedMeal)
        .filter(SavedMeal.user_id == user_id)
        .order_by(SavedMeal.created_at.desc())
        .all()
    )


def get_saved_meal_by_id(db: Session, meal_id: int, user_id: int) -> SavedMeal | None:
    """Fetch a single saved meal, scoped to the requesting user."""
    return (
        db.query(SavedMeal)
        .filter(SavedMeal.id == meal_id, SavedMeal.user_id == user_id)
        .first()
    )


def delete_saved_meal(db: Session, db_meal: SavedMeal) -> None:
    """Hard-delete a saved meal."""
    db.delete(db_meal)
    db.commit()
