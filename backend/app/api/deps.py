from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.db.models.user import User

# ── Database Dependency ────────────────────────────────────────────────────────
def get_db():
    """
    Yield a database session for the duration of a single request, then close it.

    FastAPI calls this automatically when a route declares `db: Session = Depends(get_db)`.
    The try/finally guarantees the session is always closed, even if the route raises an error.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Auth Dependency ────────────────────────────────────────────────────────────
# This tells FastAPI where clients send their token (POST /auth/login).
# FastAPI uses this to render the "Authorize" button in /docs automatically.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decode the JWT from the Authorization header and return the matching User.

    Raises HTTP 401 if:
      - The token is missing, expired, or tampered with
      - No user exists in the DB for the email encoded in the token

    Any route that declares `current_user: User = Depends(get_current_user)`
    is automatically protected — no token, no access.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = decode_access_token(token)
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Extends get_current_user by also checking the is_active flag.

    Use this instead of get_current_user on routes where a soft-banned/deactivated
    user should not be allowed through even with a valid token.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )
    return current_user
