from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import create_access_token
from app.crud.user import authenticate_user
from app.schemas.token import Token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Log in and receive a JWT access token.

    Accepts standard OAuth2 form fields — 'username' (which we treat as
    email) and 'password'. This is the format FastAPI's /docs Authorize
    button sends automatically, so the interactive docs will work out of the box.
    """
    user = authenticate_user(db, email=form_data.username, password=form_data.password)

    if user is None:
        # Deliberately vague: don't reveal whether the email exists or the password was wrong
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})

    return Token(access_token=access_token)
