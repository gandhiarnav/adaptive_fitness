from sqlalchemy.orm import Session

from app.db.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate


def get_profile_by_user_id(db: Session, user_id: int) -> Profile | None:
    """Fetch the profile belonging to a specific user."""
    return db.query(Profile).filter(Profile.user_id == user_id).first()


def create_profile(db: Session, profile_in: ProfileCreate, user_id: int) -> Profile:
    """
    Create a profile for an existing user.

    user_id is passed separately (not from the schema) because the client
    should never be able to supply or spoof it — it always comes from the
    verified JWT token via the route dependency.
    """
    db_profile = Profile(
        user_id=user_id,
        **profile_in.model_dump(),
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


def update_profile(db: Session, db_profile: Profile, profile_in: ProfileUpdate) -> Profile:
    """
    Partially update an existing profile.

    model_dump(exclude_unset=True) is the key: it only returns fields the
    client actually sent, so a PATCH with just {"weight": 80} won't wipe
    out every other field by setting them to None.
    """
    update_data = profile_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_profile, field, value)

    db.commit()
    db.refresh(db_profile)
    return db_profile
