"""Pydantic schemas for order resource."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

OrderStatusLiteral = Literal["PENDING", "PAID", "SHIPPED", "CANCELED"]


class OrderCreate(BaseModel):
    """Schema for creating an order (items and total_price)."""

    items: list[dict[str, Any]] = Field(
        default_factory=list, description="Order items"
    )
    total_price: float = Field(..., gt=0, description="Total price")


class OrderUpdate(BaseModel):
    """Schema for updating an order (status only)."""

    status: OrderStatusLiteral | None = Field(
        None,
        description="New status: PENDING, PAID, SHIPPED, CANCELED",
    )


class OrderResponse(BaseModel):
    """Schema for order in API responses."""

    id: str
    user_id: int
    items: list[dict[str, Any]]
    total_price: float
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
