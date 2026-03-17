from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Literal


# Allowed values for constrained string fields
GoalType = Literal["weight_loss", "muscle_gain", "maintenance", "endurance"]
ActivityLevel = Literal["sedentary", "lightly_active", "moderately_active", "very_active", "extra_active"]


# ── Shared foundation ──────────────────────────────────────────────────────────
class ProfileBase(BaseModel):
    height: float | None = None          # in cm
    weight: float | None = None          # in kg
    age: int | None = None
    goal: GoalType | None = None
    activity_level: ActivityLevel | None = None
    injury_flags: str | None = None      # e.g. "lower back, left knee"

    @field_validator("height")
    @classmethod
    def height_must_be_positive(cls, v: float | None) -> float | None:
        if v is not None and v <= 0:
            raise ValueError("Height must be a positive number.")
        return v

    @field_validator("weight")
    @classmethod
    def weight_must_be_positive(cls, v: float | None) -> float | None:
        if v is not None and v <= 0:
            raise ValueError("Weight must be a positive number.")
        return v

    @field_validator("age")
    @classmethod
    def age_must_be_realistic(cls, v: int | None) -> int | None:
        if v is not None and not (1 <= v <= 120):
            raise ValueError("Age must be between 1 and 120.")
        return v


# ── Incoming: create or fully replace a profile ───────────────────────────────
class ProfileCreate(ProfileBase):
    pass


# ── Incoming: partial update — every field is optional ────────────────────────
class ProfileUpdate(ProfileBase):
    pass


# ── Outgoing ──────────────────────────────────────────────────────────────────
class ProfileResponse(ProfileBase):
    id: int
    user_id: int
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
