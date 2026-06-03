from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.db.models.user import User
from app.schemas.user import UserCreate


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Fetch a single user by their primary key."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """Fetch a single user by email. Used during login and registration checks."""
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Create a new user.

    Accepts a UserCreate schema (plain password), hashes the password,
    and persists the User row. Never stores plain-text passwords.
    """
    db_user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Refreshes the object so db-generated fields (id, created_at) are populated
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Verify email + password for login.

    Returns the User if credentials are valid, None otherwise.
    The route layer decides what HTTP response to send — this function
    only answers "is this person who they say they are?"
    """
    user = get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def deactivate_user(db: Session, user: User) -> User:
    """Soft-delete: set is_active=False instead of removing the row."""
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


# ── Admin CRUD ─────────────────────────────────────────────────────────────────

def get_all_users(db: Session) -> list[User]:
    """Return every user in the database, ordered by sign-up date."""
    return db.query(User).order_by(User.created_at.desc()).all()


def toggle_user_active(db: Session, user: User) -> User:
    """Flip is_active between True and False (soft-ban / reactivate)."""
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user


def delete_user_by_id(db: Session, user_id: int) -> bool:
    """
    Hard-delete a user and all their associated data.
    Returns True if a row was deleted, False if the user wasn't found.
    """
    user = get_user_by_id(db, user_id)
    if user is None:
        return False
    db.delete(user)
    db.commit()
    return True
