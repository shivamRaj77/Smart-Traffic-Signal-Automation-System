"""
Authentication routes – register & login.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from models.user import User, add_user, get_user_by_username
from schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from services.auth_service import (
    create_access_token,
    hash_password,
    verify_password,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={409: {"description": "Username already taken"}},
)
async def register(body: RegisterRequest) -> UserResponse:
    """Create a new user account."""
    if get_user_by_username(body.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )
    user = User(
        username=body.username,
        hashed_password=hash_password(body.password),
        role=body.role,
    )
    add_user(user)
    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        created_at=user.created_at,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive a JWT",
    responses={401: {"description": "Invalid credentials"}},
)
async def login(body: LoginRequest) -> TokenResponse:
    """Validate credentials and return a bearer token."""
    user = get_user_by_username(body.username)
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token(data={"sub": user.username, "role": user.role})
    return TokenResponse(access_token=token)
