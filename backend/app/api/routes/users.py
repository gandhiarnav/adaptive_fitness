from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.crud.user import get_user_by_email, create_user
from app.db.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user account.

    Checks for duplicate email first — if it already exists we return a 409
    Conflict rather than a 400, which more accurately describes the situation.
    No auth required: this is the public sign-up endpoint.
    """
    existing = get_user_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )
    return create_user(db, user_in)


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_active_user),
):
    """
    Return the currently authenticated user's details.

    No DB call needed here — get_current_active_user already fetched
    the full User object from the database during token validation.
    """
    return current_user
