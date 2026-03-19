from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db, get_current_active_user
from app.crud.profile import get_profile_by_user_id, create_profile, update_profile
from app.db.models.user import User
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from app.services.macro_logic import compute_targets, is_profile_complete, DailyTargets

router = APIRouter(prefix="/profile", tags=["Profile"])


# ── Response schema for the targets endpoint ──────────────────────────────────
class DailyTargetsResponse(BaseModel):
    calories: int
    protein: int
    carbs: int
    fat: int
    tdee: int


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
    """
    profile = get_profile_by_user_id(db, user_id=current_user.id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create one first.",
        )
    return update_profile(db, db_profile=profile, profile_in=profile_in)


@router.get("/targets", response_model=DailyTargetsResponse)
def get_my_targets(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Compute and return personalised daily calorie and macro targets.

    Uses the Mifflin-St Jeor equation for BMR, applies the activity
    multiplier for TDEE, then adjusts for the user's goal and splits
    into protein/carbs/fat.

    Returns 404 if no profile exists yet.
    Returns 400 if the profile is incomplete (missing weight, height,
    age, activity_level, or goal).
    """
    profile = get_profile_by_user_id(db, user_id=current_user.id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create one first.",
        )

    if not is_profile_complete(
        weight_kg=profile.weight,
        height_cm=profile.height,
        age=profile.age,
        activity_level=profile.activity_level,
        goal=profile.goal,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile is incomplete. Please set weight, height, age, activity level, and goal.",
        )

    targets: DailyTargets = compute_targets(
        weight_kg=profile.weight,
        height_cm=profile.height,
        age=profile.age,
        activity_level=profile.activity_level,
        goal=profile.goal,
    )

    return DailyTargetsResponse(
        calories=targets.calories,
        protein=targets.protein,
        carbs=targets.carbs,
        fat=targets.fat,
        tdee=targets.tdee,
    )
