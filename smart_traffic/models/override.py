"""
In-memory store for admin signal-timing overrides.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class SignalOverride:
    """A manual green-time override set by an admin."""

    id: str = ""
    junction_id: str = ""
    direction: str = ""
    green_time: int = 0
    set_by: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# junction_id → direction → SignalOverride
_overrides: dict[str, dict[str, SignalOverride]] = {}

_override_counter: int = 0


def add_override(override: SignalOverride) -> SignalOverride:
    """Store an override (replaces any existing one for the same junction+direction)."""
    global _override_counter
    _override_counter += 1
    override.id = f"OVR-{_override_counter:04d}"
    _overrides.setdefault(override.junction_id, {})[override.direction] = override
    return override


def get_all_overrides() -> list[SignalOverride]:
    """Return every active override."""
    return [
        ovr
        for junc in _overrides.values()
        for ovr in junc.values()
    ]


def get_override(junction_id: str, direction: str) -> SignalOverride | None:
    """Return the override for a specific junction+direction, if any."""
    return _overrides.get(junction_id, {}).get(direction)
