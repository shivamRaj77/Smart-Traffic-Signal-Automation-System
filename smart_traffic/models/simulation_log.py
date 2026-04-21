"""Simulation log repository helpers backed by SQLAlchemy."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from db_models import SimulationLogORM
from utils.config import MAX_SIMULATION_LOGS


def add_log(db: Session, entry: dict[str, Any]) -> None:
    """Append a simulation log entry with a timestamp."""
    row = SimulationLogORM(
        timestamp=datetime.now(timezone.utc).isoformat(),
        avg_congestion=entry["avg_congestion"],
        critical_junction=entry["critical_junction"],
        critical_congestion=entry["critical_congestion"],
        triggered_by=entry.get("triggered_by", "system"),
    )
    db.add(row)
    db.commit()


def get_logs(db: Session, limit: int = 50) -> list[dict[str, Any]]:
    """Return the most recent *limit* log entries (newest first)."""
    rows = (
        db.query(SimulationLogORM)
        .order_by(SimulationLogORM.id.desc())
        .limit(min(limit, MAX_SIMULATION_LOGS))
        .all()
    )
    return [
        {
            "timestamp": r.timestamp,
            "avg_congestion": r.avg_congestion,
            "critical_junction": r.critical_junction,
            "critical_congestion": r.critical_congestion,
            "triggered_by": r.triggered_by,
        }
        for r in rows
    ]
