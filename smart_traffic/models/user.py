"""User domain model plus SQLAlchemy-backed repository helpers."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from db_models import UserORM


@dataclass
class User:
    """Represents a registered user."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    username: str = ""
    hashed_password: str = ""
    role: str = "user"  # "user" | "admin"
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def _to_domain(row: UserORM) -> User:
    return User(
        id=row.id,
        username=row.username,
        hashed_password=row.hashed_password,
        role=row.role,
        created_at=row.created_at,
    )


def get_all_users(db: Session) -> list[User]:
    """Return every registered user."""
    rows = db.query(UserORM).all()
    return [_to_domain(r) for r in rows]


def get_user_by_username(db: Session, username: str) -> User | None:
    """Look up a user by username."""
    row = db.query(UserORM).filter(UserORM.username == username).first()
    return _to_domain(row) if row else None


def get_user_by_id(db: Session, user_id: str) -> User | None:
    """Look up a user by their unique id."""
    row = db.query(UserORM).filter(UserORM.id == user_id).first()
    return _to_domain(row) if row else None


def add_user(db: Session, user: User) -> User:
    """Persist a new user."""
    row = UserORM(
        id=user.id,
        username=user.username,
        hashed_password=user.hashed_password,
        role=user.role,
        created_at=user.created_at,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    user.id = row.id
    return user


def delete_user_by_id(db: Session, user_id: str) -> bool:
    """Delete a user by id.  Returns True if found and deleted."""
    row = db.query(UserORM).filter(UserORM.id == user_id).first()
    if row is None:
        return False
    db.delete(row)
    db.commit()
    return True
