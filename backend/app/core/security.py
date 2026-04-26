from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# ── Password Hashing ───────────────────────────────────────────────────────────
# bcrypt is the industry standard: slow by design, making brute-force attacks expensive.
# We use bcrypt directly as passlib is unmaintained and conflicts with bcrypt>=4.0.0.

def hash_password(plain_password: str) -> str:
    """Take a plain-text password and return a bcrypt hash to store in the DB."""
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed_bytes.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plain-text password against a stored hash. Returns True/False."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


# ── JWT Token Generation ───────────────────────────────────────────────────────
def create_access_token(data: dict) -> str:
    """
    Create a signed JWT token.

    'data' should be {"sub": user_email} — 'sub' (subject) is the JWT standard
    claim we use to identify who the token belongs to.

    The token encodes:
      - sub: the user's email
      - exp: expiry timestamp (now + ACCESS_TOKEN_EXPIRE_MINUTES from .env)
    """
    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload.update({"exp": expire})

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """
    Decode and verify a JWT token.

    Returns the email (the 'sub' claim) if the token is valid and not expired.
    Returns None if the token is invalid or tampered with — the route dependency
    (deps.py) is responsible for turning that None into an HTTP 401.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str | None = payload.get("sub")
        return email
    except JWTError:
        return None
