"""Pydantic schemas for auth (token response)."""

from pydantic import BaseModel


class Token(BaseModel):
    """OAuth2 token response."""

    access_token: str
    token_type: str = "bearer"
