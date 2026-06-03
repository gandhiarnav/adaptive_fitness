from pydantic import BaseModel, EmailStr, field_validator, model_validator
from datetime import datetime


# ── Shared foundation ──────────────────────────────────────────────────────────
class UserBase(BaseModel):
    email: EmailStr


# ── Incoming: what the client sends to CREATE a user ──────────────────────────
class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return v


# ── Incoming: what the client sends to UPDATE their email ─────────────────────
class UserUpdate(BaseModel):
    email: EmailStr | None = None


# ── Outgoing: what we send back — hashed_password is NEVER here ───────────────
class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("is_admin", mode="before")
    @classmethod
    def coerce_is_admin(cls, v):
        """Old DB rows may have NULL for is_admin; treat that as False."""
        return bool(v) if v is not None else False
