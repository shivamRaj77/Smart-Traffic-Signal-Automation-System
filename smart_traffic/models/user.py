"""
In-memory user model and datastore.

In production this would be backed by PostgreSQL via SQLAlchemy, but for a
self-contained demo an in-memory dict is simpler to run.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field


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


# ---------------------------------------------------------------------------
# In-memory user store  (username → User)
# ---------------------------------------------------------------------------
_users: dict[str, User] = {}


def get_all_users() -> list[User]:
    """Return every registered user."""
    return list(_users.values())


def get_user_by_username(username: str) -> User | None:
    """Look up a user by username."""
    return _users.get(username)


def get_user_by_id(user_id: str) -> User | None:
    """Look up a user by their unique id."""
    for user in _users.values():
        if user.id == user_id:
            return user
    return None


def add_user(user: User) -> User:
    """Persist a new user."""
    _users[user.username] = user
    return user


def delete_user_by_id(user_id: str) -> bool:
    """Delete a user by id.  Returns True if found and deleted."""
    for uname, user in list(_users.items()):
        if user.id == user_id:
            del _users[uname]
            return True
    return False
