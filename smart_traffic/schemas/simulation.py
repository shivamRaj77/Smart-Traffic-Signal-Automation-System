"""
Pydantic schemas for the simulation endpoint responses.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class DirectionData(BaseModel):
    """Raw traffic data for one direction of a junction."""

    vehicle_count: int
    avg_speed: float


class TrafficData(BaseModel):
    """Traffic readings for all four directions."""

    north: DirectionData
    south: DirectionData
    east: DirectionData
    west: DirectionData


class CongestionData(BaseModel):
    """Normalised congestion scores per direction."""

    north: float
    south: float
    east: float
    west: float


class GreenTimes(BaseModel):
    """Allocated green-signal seconds per direction."""

    north: int
    south: int
    east: int
    west: int


class JunctionResult(BaseModel):
    """Full simulation result for a single junction."""

    junction_id: str
    traffic: TrafficData
    congestion: CongestionData
    green_times: GreenTimes
    total_congestion: float = Field(
        ..., ge=0.0, le=1.0, description="Aggregate congestion score for the junction"
    )


class AnalysisSummary(BaseModel):
    """High-level analysis across all junctions."""

    avg_congestion: float
    critical_junction: str
    critical_congestion: float
    least_congested: str
    least_congestion: float


class SimulationResponse(BaseModel):
    """Top-level response from POST /api/simulate."""

    junctions: list[JunctionResult]
    analysis: AnalysisSummary
