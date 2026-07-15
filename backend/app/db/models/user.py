from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- Active Relationships ---
    # cascade="all, delete-orphan" means: when a User is deleted,
    # their profile/journal/workout data is automatically deleted too.
    profile      = relationship("Profile",      back_populates="user", uselist=False, cascade="all, delete-orphan")
    food_journal = relationship("FoodJournal",  back_populates="user", cascade="all, delete-orphan")
    workout_logs = relationship("WorkoutLog",   back_populates="user", cascade="all, delete-orphan")