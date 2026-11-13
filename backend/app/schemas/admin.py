"""
schemas/admin.py — Admin-specific Pydantic response models
──────────────────────────────────────────────────────────
These schemas are richer than the regular UserResponse:
they embed profile info and stats alongside the base user fields.
"""

from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


class AdminUserProfile(BaseModel):
    """Embedded profile data returned alongside a user in admin views."""
    height: Optional[float] = None
    weight: Optional[float] = None
    age: Optional[int] = None
    goal: Optional[str] = None
    activity_level: Optional[str] = None
    injury_flags: Optional[str] = None

    model_config = {"from_attributes": True}


class AdminUserResponse(BaseModel):
    """
    Full user record for admin views — includes profile if it exists.
    Hashed password is NEVER included.
    """
    id: int
    email: str
    is_active: bool
    is_admin: bool = False
    created_at: datetime
    profile: Optional[AdminUserProfile] = None

    model_config = {"from_attributes": True}

    @field_validator("is_admin", mode="before")
    @classmethod
    def coerce_is_admin(cls, v):
        """Old DB rows may have NULL for is_admin; treat that as False."""
        return bool(v) if v is not None else False


class AdminStatsResponse(BaseModel):
    """Dashboard summary counters shown on the admin overview card."""
    total_users: int
    active_users: int
    admin_users: int
    total_journal_entries: int
    total_workout_logs: int


class AdminFoodJournalEntry(BaseModel):
    """Food journal row for the admin table — includes user email for context."""
    id: int
    user_id: int
    user_email: str
    date: str          # ISO date string
    raw_text_entry: str
    estimated_calories: Optional[float] = None
    estimated_protein: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminWorkoutEntry(BaseModel):
    """Workout log row for the admin table — includes user email for context."""
    id: int
    user_id: int
    user_email: str
    exercise: str
    sets: int
    reps: int
    weight: float
    date: str          # ISO date string

    model_config = {"from_attributes": True}
