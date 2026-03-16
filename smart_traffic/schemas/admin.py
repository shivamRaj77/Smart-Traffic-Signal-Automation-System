"""
Pydantic schemas for admin endpoints.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from utils.config import DIRECTIONS, JUNCTIONS


class OverrideRequest(BaseModel):
    """Body for POST /api/admin/override."""

    junction_id: str = Field(
        ...,
        examples=["J1"],
        description=f"One of {JUNCTIONS}",
    )
    direction: str = Field(
        ...,
        examples=["north"],
        description=f"One of {DIRECTIONS}",
    )
    green_time: int = Field(
        ...,
        ge=5,
        le=120,
        examples=[45],
        description="Green signal duration in seconds (5–120).",
    )


class OverrideResponse(BaseModel):
    """Persisted override record."""

    id: str
    junction_id: str
    direction: str
    green_time: int
    set_by: str
    created_at: str


class StatsResponse(BaseModel):
    """Aggregate system statistics."""

    total_users: int
    total_admins: int
    total_simulations: int
    total_overrides: int


class LogEntry(BaseModel):
    """A single simulation log entry."""

    timestamp: str
    avg_congestion: float
    critical_junction: str
    critical_congestion: float
