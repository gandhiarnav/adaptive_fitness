from pydantic import BaseModel, field_validator
from datetime import datetime


# ── Create ─────────────────────────────────────────────────────────────────────
class SavedMealCreate(BaseModel):
    name: str
    calories: float
    protein: float

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Meal name cannot be blank.")
        return v.strip()

    @field_validator("calories", "protein")
    @classmethod
    def value_must_be_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Nutritional values cannot be negative.")
        return v


# ── Response ───────────────────────────────────────────────────────────────────
class SavedMealResponse(BaseModel):
    id: int
    user_id: int
    name: str
    calories: float
    protein: float
    created_at: datetime

    model_config = {"from_attributes": True}
