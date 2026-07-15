from sqlalchemy.ext.declarative import declarative_base

# This Base class is what all your future models (User, Profile, etc.) will inherit from.
# It tells SQLAlchemy, "Hey, this Python class represents a database table!"
Base = declarative_base()