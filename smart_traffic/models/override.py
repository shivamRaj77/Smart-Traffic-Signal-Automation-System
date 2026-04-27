"""Signal override domain model and SQLAlchemy-backed repository helpers."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from db_models import SignalOverrideORM


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


def _to_domain(row: SignalOverrideORM) -> SignalOverride:
    return SignalOverride(
        id=row.id,
        junction_id=row.junction_id,
        direction=row.direction,
        green_time=row.green_time,
        set_by=row.set_by,
        created_at=row.created_at,
    )


def add_override(db: Session, override: SignalOverride) -> SignalOverride:
    """Store an override (replaces any existing one for the same junction+direction)."""
    existing = (
        db.query(SignalOverrideORM)
        .filter(
            SignalOverrideORM.junction_id == override.junction_id,
            SignalOverrideORM.direction == override.direction,
        )
        .first()
    )

    if existing is not None:
        existing.green_time = override.green_time
        existing.set_by = override.set_by
        db.commit()
        db.refresh(existing)
        return _to_domain(existing)

    if not override.id:
        override.id = f"OVR-{uuid.uuid4().hex[:8].upper()}"

    row = SignalOverrideORM(
        id=override.id,
        junction_id=override.junction_id,
        direction=override.direction,
        green_time=override.green_time,
        set_by=override.set_by,
        created_at=override.created_at,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    override.id = row.id
    return override


def get_all_overrides(db: Session) -> list[SignalOverride]:
    """Return every active override."""
    rows = db.query(SignalOverrideORM).all()
    return [_to_domain(r) for r in rows]


def get_override(db: Session, junction_id: str, direction: str) -> SignalOverride | None:
    """Return the override for a specific junction+direction, if any."""
    row = (
        db.query(SignalOverrideORM)
        .filter(
            SignalOverrideORM.junction_id == junction_id,
            SignalOverrideORM.direction == direction,
        )
        .first()
    )
    return _to_domain(row) if row else None
