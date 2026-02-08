"""Authentication routes: registration and token (OAuth2 Password Flow)."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="", tags=["auth"])


@router.post(
    "/register/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Create a user with email and hashed password. Returns 409 if email exists."""
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/token/",
    response_model=Token,
    summary="OAuth2 password flow login",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Accept username (email) and password; return JWT access token or 401."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if user is None or not verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(sub=user.id)
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/users/me/",
    response_model=UserResponse,
    summary="Get current user",
)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user (protected route)."""
    return current_user
