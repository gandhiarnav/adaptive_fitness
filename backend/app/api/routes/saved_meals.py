from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.crud.saved_meal import (
    create_saved_meal,
    get_saved_meals,
    get_saved_meal_by_id,
    delete_saved_meal,
)
from app.db.models.user import User
from app.schemas.saved_meal import SavedMealCreate, SavedMealResponse

router = APIRouter(prefix="/meals/saved", tags=["Saved Meals"])


@router.get("/", response_model=list[SavedMealResponse])
def list_saved_meals(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Return all saved meals for the current user, newest first."""
    return get_saved_meals(db, user_id=current_user.id)


@router.post("/", response_model=SavedMealResponse, status_code=status.HTTP_201_CREATED)
def create_saved_meal_route(
    meal_in: SavedMealCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Save a new reusable meal template for the current user."""
    return create_saved_meal(db, meal_in=meal_in, user_id=current_user.id)


@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_meal_route(
    meal_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a saved meal. Users can only delete their own meals."""
    meal = get_saved_meal_by_id(db, meal_id=meal_id, user_id=current_user.id)
    if meal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved meal not found.",
        )
    delete_saved_meal(db, db_meal=meal)
