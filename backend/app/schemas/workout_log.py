from pydantic import BaseModel, field_validator
from datetime import date


# ── Shared foundation ──────────────────────────────────────────────────────────
class WorkoutLogBase(BaseModel):
    exercise: str
    sets: int
    reps: int
    weight: float
    date: date

    @field_validator("exercise")
    @classmethod
    def exercise_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Exercise name cannot be blank.")
        return v.strip()

    @field_validator("sets", "reps")
    @classmethod
    def must_be_positive_int(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Sets and reps must be positive integers.")
        return v

    @field_validator("weight")
    @classmethod
    def weight_must_be_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Weight cannot be negative (use 0 for bodyweight exercises).")
        return v


# ── Incoming ───────────────────────────────────────────────────────────────────
class WorkoutLogCreate(WorkoutLogBase):
    pass


# ── Incoming: partial update — all fields optional ────────────────────────────
class WorkoutLogUpdate(BaseModel):
    exercise: str | None = None
    sets: int | None = None
    reps: int | None = None
    weight: float | None = None
    date: date | None = None


# ── Outgoing ──────────────────────────────────────────────────────────────────
class WorkoutLogResponse(WorkoutLogBase):
    id: int
    user_id: int

    model_config = {"from_attributes": True}
