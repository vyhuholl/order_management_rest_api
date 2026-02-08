"""Order persistence model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class OrderStatus:
    """Order status enum values."""

    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELED = "CANCELED"


class Order(Base):
    """Order model: UUID id, user_id FK, items JSON, total_price, status, created_at."""

    __tablename__ = "orders"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    items = Column(JSON, nullable=False, default=list)
    total_price = Column(Float, nullable=False)
    status = Column(
        Enum(
            "PENDING",
            "PAID",
            "SHIPPED",
            "CANCELED",
            name="order_status",
            create_constraint=True,
        ),
        nullable=False,
        default="PENDING",
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", backref="orders")
