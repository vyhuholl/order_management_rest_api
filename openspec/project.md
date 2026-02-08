# Project Context

## Purpose

A REST API service for managing orders in an e-commerce context. The service provides user authentication, order creation, order retrieval, and order status updates. Orders are processed asynchronously using an event-driven architecture with RabbitMQ and Celery. Redis is used for caching order data to improve performance.

## Tech Stack

### Core Framework
- **FastAPI** - Modern, fast web framework for building APIs
- **Pydantic** - Data validation using Python type annotations

### Database & ORM
- **PostgreSQL** - Primary relational database
- **SQLAlchemy** - Python SQL toolkit and ORM
- **Alembic** - Database migration tool

### Authentication & Security
- **OAuth2 Password Flow** - JWT-based authentication
- **PyJWT** - JWT token creation and validation
- **pwdlib** - Password hashing

### Messaging & Background Tasks
- **RabbitMQ** - Message broker for event-driven architecture
- **pika** - RabbitMQ client library
- **Celery** - Distributed task queue for background processing

### Caching
- **Redis** - In-memory data store for order caching

### Development Tools
- **uv** - Fast Python package installer and runner
- **python-dotenv** - Environment variable management
- **slowapi** - Rate limiting middleware
- **pytest** - Testing framework
- **pytest-cov** - Code coverage plugin for pytest
- **ruff** - Fast Python linter and formatter

### Deployment
- **Docker** - Containerization
- **docker-compose** - Multi-container orchestration
- Base image: `ghcr.io/astral-sh/uv:python3.14-alpine`

## Project Conventions

### Code Style

- **Line Length**: 79 characters (enforced by ruff)
- **Style Guide**: PEP 8 with ruff-specific rules
- **Formatting**: Use `ruff-format` for code formatting
- **Linting**: Use `ruff` for linting (excludes `alembic` directory)
- **Documentation**: All code must have readable docstrings
- **Command Execution**: All Python code, ruff, and pytest commands must be run via `uv run`

### Architecture Patterns

#### API Design
- RESTful API design with clear resource endpoints
- OAuth2 Password Flow for JWT-based authentication
- CORS middleware enabled for cross-origin requests

#### Database
- SQLAlchemy ORM with declarative base
- UUID primary keys for orders
- Integer primary keys for users
- Foreign key relationships with proper constraints
- JSON fields for flexible data storage (order items)
- Enum fields for status tracking

#### Event-Driven Architecture
- RabbitMQ as event bus for decoupled communication
- `new_order` events published to task queue on order creation
- Celery consumers subscribe to queue and process messages
- Background tasks for asynchronous order processing

#### Caching Strategy
- Redis for order data caching
- 5-minute TTL for cached orders
- Cache-first lookup: check Redis before database
- Cache invalidation on order updates

### Testing Strategy

- **Test-First Development**: Write tests before implementation
- **Testing Framework**: pytest
- **Coverage**: Aim for at least 80% code coverage (measured with pytest-cov)
- **Test Organization**: Tests should be co-located with source code or in dedicated test directory
- **Test Execution**: Run tests via `uv run pytest`

### Git Workflow

- **Branching Strategy**: Single master branch for everything
- **Commit Conventions**: Use clear, descriptive commit messages
- **Pull Requests**: Review and merge changes directly to master

### Command Conventions

```bash
# Install dependencies
uv sync

# Run the application
uv run uvicorn app.main:app --reload

# Run linter
uv run ruff check .

# Format code
uv run ruff format .

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=app --cov-report=html

# Create database migration
uv run alembic revision --autogenerate -m "description"

# Apply database migration
uv run alembic upgrade head

# Run Celery worker
uv run celery -A app.tasks.celery_app worker --loglevel=info
```

## Domain Context

### Order Lifecycle

Orders progress through the following states:
- **PENDING**: Initial state after order creation
- **PAID**: Payment confirmed
- **SHIPPED**: Order has been shipped to customer
- **CANCELED**: Order was canceled

### Order Structure

An order contains:
- Unique identifier (UUID)
- Associated user (foreign key to users table)
- List of items (JSON array)
- Total price (float)
- Current status (enum)
- Creation timestamp

### User Management

Users are registered with email and password. Passwords are hashed before storage. Users authenticate via OAuth2 Password Flow to receive JWT access tokens for authorized operations.

## Important Constraints

### Security Requirements

- **Authentication**: JWT-based authentication (OAuth2 Password Flow) required for order creation and user-specific order retrieval
- **Password Security**: All passwords must be hashed using pwdlib
- **Rate Limiting**: API limited to 5 requests per minute per client
- **CORS**: CORS middleware must be enabled
- **Environment Variables**: All sensitive data must be stored in `.env` file and loaded via python-dotenv

### Performance Requirements

- **Caching**: Order data cached in Redis with 5-minute TTL
- **Background Processing**: Order processing handled asynchronously by Celery
- **Cache-First**: Always check Redis cache before querying database for order data

### Code Quality Requirements

- **Coverage**: Minimum 80% test coverage
- **Documentation**: All code must have docstrings
- **Linting**: Code must pass ruff checks
- **Formatting**: Code must be formatted with ruff-format

## External Dependencies

### Services

- **PostgreSQL**: Primary database for persistent storage
- **RabbitMQ**: Message broker for event-driven communication
- **Redis**: In-memory cache for order data

### Required Environment Variables

```env
# Database
DATABASE_URL=postgresql://ecommerce_user:ecommerce_password@postgres:5432/ecommerce_db

# Redis
REDIS_URL=redis://localhost:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# JWT Secret
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Application
APP_HOST=0.0.0.0
APP_PORT=8000
```

### API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register/` | User registration (email and password) | No |
| POST | `/token/` | Login for access token (OAuth2) | No |
| POST | `/orders/` | Order creation | Yes |
| GET | `/orders/{order_id}` | Get order information (cache-first) | Yes |
| PATCH | `/orders/{order_id}` | Update order status | Yes |
| GET | `/orders/user/{user_id}` | Get all orders for a user | Yes |

### Database Schema

#### Users Table
- `id` (int, primary key)
- `email` (varchar, unique)
- `hashed_password` (varchar)

#### Orders Table
- `id` (UUID, primary key)
- `user_id` (int, foreign key → users.id)
- `items` (JSON, list of items)
- `total_price` (float)
- `status` (enum: PENDING, PAID, SHIPPED, CANCELED)
- `created_at` (datetime)

### Event Bus

- **Event**: `new_order`
- **Queue**: Task queue for order processing
- **Consumer**: Celery worker that processes orders with 2-second delay and prints confirmation
