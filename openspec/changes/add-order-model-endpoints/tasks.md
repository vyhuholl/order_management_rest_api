# Tasks: Add Order model and order-related endpoints

## 1. Order model and persistence

- [x] 1.1 Add SQLAlchemy Order model (UUID id, user_id FK to users, items JSON, total_price float, status enum, created_at). Register enum (PENDING, PAID, SHIPPED, CANCELED).
- [x] 1.2 Create Alembic revision for orders table and apply upgrade.
- [x] 1.3 Add Pydantic schemas for orders (e.g. OrderCreate with items and total_price, OrderUpdate with optional status, OrderResponse with id, user_id, items, total_price, status, created_at).

## 2. Caching and events

- [x] 2.1 Add Redis client and config (e.g. REDIS_URL). Implement cache get/set/delete for order by id with 5-minute TTL.
- [x] 2.2 Implement RabbitMQ publisher (pika): publish new_order event (order id, user_id) to configured task queue on order creation. Document queue name and payload shape.

## 3. Order service / repository

- [x] 3.1 Implement order repository or service: create order (DB + publish event), get by id (cache-first: Redis then DB, set cache on DB read), update status (DB + invalidate cache), list by user_id. Enforce ownership (order.user_id == current user id) for get, update, and list.

## 4. Order API

- [x] 4.1 Implement POST /orders/: require JWT; accept body (items, total_price); create order; publish new_order; return 201 with order representation. Return 401 when unauthenticated.
- [x] 4.2 Implement GET /orders/{order_id}: require JWT; cache-first retrieval; return order only if owned by current user; 404 otherwise; 401 when unauthenticated.
- [x] 4.3 Implement PATCH /orders/{order_id}: require JWT; accept body (status); update only if owned by current user; invalidate cache; return updated order or 404/401.
- [x] 4.4 Implement GET /orders/user/{user_id}: require JWT; return list of orders only when path user_id matches current user id; 403 when user_id does not match; 401 when unauthenticated.
- [x] 4.5 Mount order routes under /orders (or as defined), add OpenAPI tags/summaries.

## 5. Validation and tests

- [x] 5.1 Add tests for order creation (success, unauthenticated).
- [x] 5.2 Add tests for get order by id (cache hit/miss, own order, other user's order, 404, 401).
- [x] 5.3 Add tests for PATCH order (success, 404 for other user, 401).
- [x] 5.4 Add tests for list orders by user (own user, 403 for other user_id, 401).
- [x] 5.5 Add tests for cache invalidation on update and for new_order event publish on create (e.g. mock or integration as appropriate).
- [x] 5.6 Run `uv run pytest` and ensure coverage remains acceptable; run `uv run ruff check .` and `uv run ruff format .`.
