from pydantic import BaseModel, field_validator
from datetime import date, datetime


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


# ── Outgoing: includes the AI-estimated fields the client never sends ──────────
class FoodJournalResponse(FoodJournalBase):
    id: int
    user_id: int
    estimated_calories: int | None = None
    estimated_protein: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
