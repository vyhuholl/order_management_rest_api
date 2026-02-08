# E-Commerce REST API

A FastAPI-based REST API service for managing orders with event-driven architecture.

## Prerequisites

- Docker and Docker Compose

## Quick Start with Docker

1. **Clone the repository and navigate to the project directory**

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   Update the `.env` file with your configuration (especially `JWT_SECRET_KEY` for production).

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

   This will start:
   - PostgreSQL database (port 5432)
   - Redis cache (port 6379)
   - RabbitMQ message broker (ports 5672, 15672)
   - FastAPI application (port 8000)
   - Celery worker for background tasks

4. **Check service health**
   ```bash
   docker-compose ps
   ```

5. **View logs**
   ```bash
   # All services
   docker-compose logs -f

   # Specific service
   docker-compose logs -f app
   docker-compose logs -f celery_worker
   ```

6. **Access the application**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - RabbitMQ Management UI: http://localhost:15672 (guest/guest)

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register/` | User registration | No |
| POST | `/token/` | Login for access token | No |
| POST | `/orders/` | Create order | Yes |
| GET | `/orders/{order_id}` | Get order information | Yes |
| PATCH | `/orders/{order_id}` | Update order status | Yes |
| GET | `/orders/user/{user_id}` | Get all orders for user | Yes |

## Environment Variables

See `.env.example` for all available configuration options.

**Important**: Change `JWT_SECRET_KEY` to a secure random value in production!

## Architecture

- **FastAPI**: Web framework for REST API
- **PostgreSQL**: Primary database
- **Redis**: Caching layer (5-minute TTL)
- **RabbitMQ**: Message broker for event-driven architecture
- **Celery**: Background task processing
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration tool

## Security

- JWT-based authentication (OAuth2 Password Flow)
- Password hashing with pwdlib
- Rate limiting: 5 requests per minute per client
- CORS enabled

## License

This project a test assignment for backend developer position.