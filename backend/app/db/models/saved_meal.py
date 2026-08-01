from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class SavedMeal(Base):
    __tablename__ = "saved_meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)          # e.g. "Dal Chawal", "Post-Workout Shake"
    calories = Column(Float, nullable=False)        # kcal — Float for decimal support
    protein = Column(Float, nullable=False)         # grams — Float for decimal support

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to the User
    user = relationship("User", back_populates="saved_meals")
