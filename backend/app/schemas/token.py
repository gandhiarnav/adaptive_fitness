from pydantic import BaseModel


# ── What the /login endpoint returns ──────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── The decoded payload that lives inside a JWT ───────────────────────────────
# "sub" (subject) is the JWT standard claim — we store the user's email here.
class TokenData(BaseModel):
    email: str | None = None
