"""
In-memory circular buffer for simulation logs.
"""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Any

from utils.config import MAX_SIMULATION_LOGS

# Fixed-size deque acts as a ring buffer
_logs: deque[dict[str, Any]] = deque(maxlen=MAX_SIMULATION_LOGS)


def add_log(entry: dict[str, Any]) -> None:
    """Append a simulation log entry with a timestamp."""
    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    _logs.append(entry)


def get_logs(limit: int = 50) -> list[dict[str, Any]]:
    """Return the most recent *limit* log entries (newest first)."""
    return list(reversed(_logs))[:limit]
