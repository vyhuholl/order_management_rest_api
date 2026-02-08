"""Order routes: create, get by id, update status, list by user. All require JWT."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.services.order_service import (
    create_order,
    get_order_by_id,
    list_orders_by_user,
    update_order_status,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an order",
)
def post_order(
    body: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create an order for the authenticated user; publish new_order event. 401 if unauthenticated."""
    order = create_order(db, user_id=current_user.id, data=body)
    return OrderResponse.model_validate(order)


@router.get(
    "/user/{user_id}",
    response_model=list[OrderResponse],
    summary="List orders for a user",
)
def list_orders(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List orders for user_id. Only when path user_id matches current user; 403 otherwise. 401 if unauthenticated."""
    orders = list_orders_by_user(
        db, user_id=user_id, current_user_id=current_user.id
    )
    if orders is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to list another user's orders",
        )
    return [OrderResponse.model_validate(o) for o in orders]


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order by ID",
)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get order by id (cache-first). Only own order; 404 otherwise. 401 if unauthenticated."""
    data = get_order_by_id(
        db, order_id=order_id, current_user_id=current_user.id
    )
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return OrderResponse.model_validate(data)


@router.patch(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Update order status",
)
def patch_order(
    order_id: str,
    body: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update order status only if owned by current user; invalidate cache. 404/401 otherwise."""
    order = update_order_status(
        db, order_id=order_id, current_user_id=current_user.id, data=body
    )
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return OrderResponse.model_validate(order)
