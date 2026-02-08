# orders Specification

## Purpose
TBD - created by archiving change add-order-model-endpoints. Update Purpose after archive.
## Requirements
### Requirement: Order persistence model

The system SHALL persist orders in a relational store with a UUID primary key, a foreign key to the users table, items as a JSON field, total_price, status as an enum, and a creation timestamp. The model SHALL support lookup by id and by user_id.

#### Scenario: Order record has required fields

- **GIVEN** an order has been created for a user with items and total price
- **THEN** the stored record SHALL have a UUID id, user_id (foreign key to users.id), items (JSON array), total_price (float), status (one of PENDING, PAID, SHIPPED, CANCELED), and created_at (datetime)
- **AND** the order SHALL be retrievable by id and by user_id

#### Scenario: Status restricted to allowed values

- **WHEN** an order is created or updated
- **THEN** status SHALL be one of PENDING, PAID, SHIPPED, CANCELED
- **AND** the system SHALL reject or constrain any other value

### Requirement: Order creation endpoint

The system SHALL expose a POST endpoint for creating orders. The endpoint SHALL require a valid JWT. The request body SHALL include items and total price; the system SHALL persist the order, associate it with the authenticated user, publish a new_order event to the message broker, and return the created order (e.g. 201 with order representation).

#### Scenario: Order created with valid auth and body

- **WHEN** a client sends POST to the orders endpoint with a valid Bearer JWT and a body containing items and total_price
- **THEN** the system SHALL create an order with status PENDING, user_id equal to the authenticated user's id, and SHALL respond with 201 and a representation of the created order (id, user_id, items, total_price, status, created_at)
- **AND** SHALL publish a new_order event (e.g. order id and user_id) to the configured RabbitMQ task queue

#### Scenario: Order creation rejected without auth

- **WHEN** a client sends POST to the orders endpoint without a valid Bearer JWT
- **THEN** the system SHALL respond with 401 Unauthorized
- **AND** SHALL NOT create an order or publish an event

### Requirement: Order retrieval by ID

The system SHALL expose a GET endpoint to retrieve a single order by id. The endpoint SHALL require a valid JWT. The system SHALL use a cache-first strategy (Redis then database). The order SHALL be returned only if it belongs to the authenticated user; otherwise the system SHALL respond with 404.

#### Scenario: Own order returned from cache or database

- **WHEN** a client sends GET with a valid JWT for an order id that exists and belongs to the authenticated user
- **THEN** the system SHALL return the order (e.g. id, user_id, items, total_price, status, created_at)
- **AND** SHALL look up the order from cache first; if not in cache, from the database, and SHALL populate cache when read from database

#### Scenario: Other user's order or missing order returns 404

- **WHEN** a client sends GET with a valid JWT for an order id that does not exist or belongs to another user
- **THEN** the system SHALL respond with 404 Not Found
- **AND** SHALL NOT return order data

#### Scenario: Unauthorized request rejected

- **WHEN** a client sends GET without a valid Bearer JWT
- **THEN** the system SHALL respond with 401 Unauthorized

### Requirement: Order status update

The system SHALL expose a PATCH endpoint to update an order's status. The endpoint SHALL require a valid JWT. The order MAY be updated only if it belongs to the authenticated user. On successful update the system SHALL invalidate the order's cache entry.

#### Scenario: Own order status updated

- **WHEN** a client sends PATCH with a valid JWT for an order id that belongs to the authenticated user and a body containing a valid status (e.g. PAID, SHIPPED, CANCELED)
- **THEN** the system SHALL update the order's status
- **AND** SHALL invalidate the cached order for that id
- **AND** SHALL respond with the updated order representation

#### Scenario: Other user's order or missing order returns 404

- **WHEN** a client sends PATCH with a valid JWT for an order id that does not exist or belongs to another user
- **THEN** the system SHALL respond with 404 Not Found
- **AND** SHALL NOT update any order

#### Scenario: Unauthorized request rejected

- **WHEN** a client sends PATCH without a valid Bearer JWT
- **THEN** the system SHALL respond with 401 Unauthorized

### Requirement: List orders by user

The system SHALL expose a GET endpoint to list orders for a user. The endpoint SHALL require a valid JWT. The system SHALL return only orders for the authenticated user; the path user_id SHALL match the authenticated user's id, otherwise the system SHALL respond with 403 or return only the authenticated user's orders as defined by implementation.

#### Scenario: User lists own orders

- **WHEN** a client sends GET for orders of a user with a valid JWT and the path user_id matches the JWT subject (authenticated user id)
- **THEN** the system SHALL return a list of orders belonging to that user (e.g. array of order representations)
- **AND** SHALL NOT include orders of other users

#### Scenario: Request for another user's orders forbidden

- **WHEN** a client sends GET for orders of a user_id that does not match the authenticated user's id
- **THEN** the system SHALL respond with 403 Forbidden
- **AND** SHALL NOT return any order data

#### Scenario: Unauthorized request rejected

- **WHEN** a client sends GET without a valid Bearer JWT
- **THEN** the system SHALL respond with 401 Unauthorized

### Requirement: Order data caching

The system SHALL cache order-by-ID data in Redis. Reads for a single order by id SHALL check the cache first; on cache miss the system SHALL load from the database and SHALL set the cache. Cached entries SHALL have a TTL of 5 minutes. The system SHALL invalidate the cache for an order when that order is updated (e.g. PATCH).

#### Scenario: Cache hit returns cached order

- **GIVEN** an order is in the Redis cache for its id
- **WHEN** a valid request to get that order by id is processed
- **THEN** the system SHALL return the order from cache without querying the database for that read

#### Scenario: Cache miss loads from database and sets cache

- **GIVEN** an order exists in the database but not in cache
- **WHEN** a valid request to get that order by id is processed
- **THEN** the system SHALL load the order from the database
- **AND** SHALL store it in Redis with a 5-minute TTL
- **AND** SHALL return the order

#### Scenario: Cache invalidated on order update

- **GIVEN** an order is in the Redis cache
- **WHEN** that order is successfully updated (e.g. via PATCH)
- **THEN** the system SHALL remove or invalidate the cache entry for that order id
- **AND** subsequent reads for that order SHALL load from database and repopulate cache as needed

### Requirement: New order event publishing

The system SHALL publish a new_order event to the configured RabbitMQ task queue when an order is successfully created. The event payload SHALL include at least the order id and user_id so that consumers (e.g. Celery) can process the order asynchronously.

#### Scenario: Event published on order creation

- **WHEN** an order is successfully created via the POST orders endpoint
- **THEN** the system SHALL publish a message to the configured RabbitMQ queue (e.g. new_order or task queue)
- **AND** the message SHALL include the created order's id and user_id (or equivalent payload sufficient for consumers)

#### Scenario: No event on creation failure

- **WHEN** order creation fails (e.g. validation or persistence error)
- **THEN** the system SHALL NOT publish a new_order event

