"""Pydantic schemas for user resource."""

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema for creating a user (registration)."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user in API responses (no password)."""

    id: int
    email: str

    model_config = {"from_attributes": True}
