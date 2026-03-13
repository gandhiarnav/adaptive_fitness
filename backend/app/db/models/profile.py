from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    height = Column(Float) # In cm or inches (you can decide later)
    weight = Column(Float)
    age = Column(Integer)
    goal = Column(String)
    activity_level = Column(String)
    injury_flags = Column(String)
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship back to the User
    user = relationship("User", back_populates="profile")