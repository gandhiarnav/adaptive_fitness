from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 1. Create the database engine
# Note: "check_same_thread": False is needed ONLY for SQLite in FastAPI.
# When you upgrade to PostgreSQL later, you will remove that specific connect_arg.
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)

# 2. Create a SessionLocal class
# Each instance of this class will be an actual database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)