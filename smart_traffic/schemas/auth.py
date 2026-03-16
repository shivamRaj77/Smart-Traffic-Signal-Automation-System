"""
Pydantic request / response schemas for authentication endpoints.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """Body for POST /api/auth/register."""

    username: str = Field(..., min_length=3, max_length=32, examples=["john_doe"])
    password: str = Field(..., min_length=6, max_length=128, examples=["securePass1!"])
    role: str = Field(
        default="user",
        pattern="^(user|admin)$",
        examples=["user"],
        description="Either 'user' or 'admin'.",
    )


class LoginRequest(BaseModel):
    """Body for POST /api/auth/login."""

    username: str = Field(..., examples=["admin"])
    password: str = Field(..., examples=["admin123"])


class TokenResponse(BaseModel):
    """Returned on successful login."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Public representation of a user."""

    id: str
    username: str
    role: str
    created_at: str
