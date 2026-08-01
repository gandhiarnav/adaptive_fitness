from sqlalchemy import Column, Boolean, Integer, Float, String, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class FoodJournal(Base):
    __tablename__ = "food_journal"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    date = Column(Date, nullable=False)
    raw_text_entry = Column(String, nullable=False) # e.g., "Ate an apple and 2 eggs"
    is_manual = Column(Boolean, default=False, nullable=False, server_default="0")
    estimated_calories = Column(Float)   # kcal — Float supports decimals
    estimated_protein = Column(Float)    # grams — Float supports decimals
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to the User
    user = relationship("User", back_populates="food_journal")