# Design: Order model and endpoints

## Context

The API must support creating orders, retrieving them by ID (with performance via caching), updating order status, and listing orders per user. Orders are owned by users (existing User model). Project conventions require Redis for order caching, RabbitMQ for `new_order` events, and JWT for protecting all order endpoints.

## Goals / Non-Goals

- **Goals**: Persist orders with correct schema; expose REST endpoints with auth and ownership checks; cache order-by-ID in Redis with invalidation on update; publish `new_order` to RabbitMQ on creation.
- **Non-Goals**: Implementing the Celery consumer that processes `new_order` (can be same or follow-up change); payment or shipping provider integration; order items as a separate table (use JSON per project).

## Decisions

- **Order primary key**: UUID. Aligns with project.md; avoids exposing sequential IDs.
- **Order items**: Single JSON column (list of items). Matches project.md and keeps schema simple; no separate line-items table for this change.
- **Status**: Enum (PENDING, PAID, SHIPPED, CANCELED) as in project.md.
- **Caching**: Redis key per order ID; 5-minute TTL; cache invalidation on PATCH. Lookup order: check Redis first, then DB; on read-from-DB, set cache.
- **Events**: On successful order creation, publish `new_order` event (e.g. order id, user_id) to the configured RabbitMQ queue using pika. Consumer implementation (Celery) is out of scope of this proposal’s implementation tasks but the contract (queue name, payload shape) SHALL be documented.
- **Ownership**: All order endpoints require valid JWT. GET by ID and PATCH allow access only when `order.user_id` equals the authenticated user’s id. GET list by user returns orders only when path `user_id` matches the authenticated user’s id.

## Risks / Trade-offs

- **Cache invalidation**: If multiple instances update the same order, invalidation must run on every update to avoid stale reads. Standard delete-key on PATCH suffices.
- **Event at-least-once**: RabbitMQ guarantees delivery; duplicate processing is a consumer concern. No change to broker semantics in this proposal.

## Migration Plan

- Add Alembic revision for `orders` table after users table exists. No backfill. Rollback: downgrade drops `orders` table.

## Open Questions

- None for the proposal scope.
