"""
Authentication service layer.

Handles password hashing, JWT creation / verification, and the default
admin bootstrap.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from models.user import User, add_user, get_user_by_username
from utils.config import (
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_USERNAME,
    SECRET_KEY,
)

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain*."""
    return _pwd_ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Check *plain* against a bcrypt *hashed* value."""
    return _pwd_ctx.verify(plain, hashed)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT containing *data*."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and verify a JWT.  Raises HTTPException on failure."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------------------------------------------------------------------------
# Dependency: current user from bearer token
# ---------------------------------------------------------------------------

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """FastAPI dependency – resolve the authenticated user from the JWT."""
    payload = decode_token(token)
    username: str | None = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Token missing subject claim")
    user = get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """FastAPI dependency – ensures the caller is an admin."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

def create_default_admin() -> None:
    """Idempotently create the default admin account."""
    if get_user_by_username(DEFAULT_ADMIN_USERNAME) is None:
        admin = User(
            username=DEFAULT_ADMIN_USERNAME,
            hashed_password=hash_password(DEFAULT_ADMIN_PASSWORD),
            role="admin",
        )
        add_user(admin)
