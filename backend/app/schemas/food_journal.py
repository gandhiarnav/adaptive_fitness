from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional


# ── Shared foundation ──────────────────────────────────────────────────────────
class FoodJournalBase(BaseModel):
    date: date
    raw_text_entry: str

    @field_validator("raw_text_entry")
    @classmethod
    def entry_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Food journal entry cannot be blank.")
        return v.strip()


# ── Incoming: AI-mode (text → estimator) ───────────────────────────────────────
class FoodJournalCreate(FoodJournalBase):
    """Client sends raw text; the AI service layer will fill in the macro estimates."""
    pass


# ── Incoming: Manual-mode (user supplies macros directly) ─────────────────────
class FoodJournalManualCreate(FoodJournalBase):
    """
    Client explicitly provides calorie and protein values.
    The AI estimator is skipped entirely for this path.
    """
    manual_calories: float
    manual_protein: float

    @field_validator("manual_calories", "manual_protein")
    @classmethod
    def value_must_be_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Nutritional values cannot be negative.")
        return v


# ── Update: what the client sends for PATCH ────────────────────────────────────
class FoodJournalUpdate(BaseModel):
    raw_text_entry: Optional[str] = None
    date: Optional[date] = None

    @field_validator("raw_text_entry")
    @classmethod
    def entry_must_not_be_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Food journal entry cannot be blank.")
        return v.strip() if v is not None else v


# ── Outgoing: includes the AI-estimated (or manual) fields ────────────────────
class FoodJournalResponse(FoodJournalBase):
    id: int
    user_id: int
    is_manual: bool = False
    estimated_calories: float | None = None   # Float for decimal support
    estimated_protein: float | None = None    # Float for decimal support
    created_at: datetime

    model_config = {"from_attributes": True}
