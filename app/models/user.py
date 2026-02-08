"""User model for authentication and authorization."""

from sqlalchemy import Column, Integer, String

from app.core.database import Base


class User(Base):
    """User persistence model with email and hashed password."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
