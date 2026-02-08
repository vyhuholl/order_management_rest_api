"""Main application module."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Create rate limiter instance
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="E-Commerce Order API",
    description="REST API for managing e-commerce orders",
    version="1.0.0",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Allowed CORS origins – configure appropriately for production
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:8080",
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
@limiter.limit("5/minute")
async def root():
    """Root endpoint to verify API is running."""
    return {"message": "E-Commerce Order API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
