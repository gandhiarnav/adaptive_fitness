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


# ── Incoming: what the client sends ───────────────────────────────────────────
# The client sends raw text; the AI service layer will fill in the macro estimates.
class FoodJournalCreate(FoodJournalBase):
    pass


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


# ── Outgoing: includes the AI-estimated fields the client never sends ──────────
class FoodJournalResponse(FoodJournalBase):
    id: int
    user_id: int
    estimated_calories: int | None = None
    estimated_protein: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
