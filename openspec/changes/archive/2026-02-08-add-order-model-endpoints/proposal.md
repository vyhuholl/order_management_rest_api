# Change: Add Order model and order-related endpoints

## Why

The API has user authentication but no order resource. The service exists to manage e-commerce orders; adding an Order model and REST endpoints for creating, retrieving, updating, and listing orders (with caching and event publishing) delivers the core order-management behavior described in project conventions.

## What Changes

- Introduce an **Order** persistence model: UUID primary key, `user_id` (foreign key to users), `items` (JSON), `total_price`, `status` (enum: PENDING, PAID, SHIPPED, CANCELED), `created_at`.
- Add **order creation**: `POST /orders/` (auth required); accept items and total price; persist order; publish `new_order` event to RabbitMQ; return 201 with order representation.
- Add **order retrieval by ID**: `GET /orders/{order_id}` (auth required); cache-first (Redis then database); return order only if it belongs to the authenticated user; 404 otherwise.
- Add **order status update**: `PATCH /orders/{order_id}` (auth required); accept status; update only if order belongs to user; invalidate cache on update.
- Add **list orders by user**: `GET /orders/user/{user_id}` (auth required); return only orders for the authenticated user (user_id in path must match token).
- Implement **order data caching**: Redis cache for order-by-ID with 5-minute TTL; cache invalidation on order update.
- Add Alembic migration for the orders table and wire order routes into the FastAPI app.

## Impact

- **Affected specs**: New capability `orders` (no existing orders spec).
- **Affected code**: New `app/models/order.py`, `app/schemas/order.py`, `app/routes/orders.py` (or equivalent), order service/repository for cache and DB, RabbitMQ event publishing, `app/main.py` (router inclusion), new Alembic revision. Depends on existing `auth` (JWT) and `users` (user_id) capabilities.
