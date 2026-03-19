from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.crud.profile import get_profile_by_user_id, create_profile, update_profile
from app.db.models.user import User
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/", response_model=ProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Return the current user's profile. 404 if they haven't created one yet."""
    profile = get_profile_by_user_id(db, user_id=current_user.id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create one first.",
        )
    return profile


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_my_profile(
    profile_in: ProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a profile for the current user.

    Returns 409 if they already have one — a user can only have one profile
    (enforced at the DB level too via the unique constraint on user_id).
    """
    existing = get_profile_by_user_id(db, user_id=current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists. Use PATCH to update it.",
        )
    return create_profile(db, profile_in=profile_in, user_id=current_user.id)


@router.patch("/", response_model=ProfileResponse)
def update_my_profile(
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Partially update the current user's profile.

    Only the fields included in the request body will be changed.
    Returns 404 if the profile doesn't exist yet.
    """
    profile = get_profile_by_user_id(db, user_id=current_user.id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create one first.",
        )
    return update_profile(db, db_profile=profile, profile_in=profile_in)
