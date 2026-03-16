"""
Simulation endpoint – runs the traffic engine and returns results.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from models.simulation_log import add_log
from models.user import User
from schemas.simulation import SimulationResponse
from services.auth_service import get_current_user
from services.traffic_service import run_simulation

router = APIRouter()

# Module-level counter so admin stats can reference it
simulation_count: int = 0


@router.post(
    "/simulate",
    response_model=SimulationResponse,
    summary="Run one simulation tick for all 9 junctions",
    responses={401: {"description": "Not authenticated"}},
)
async def simulate(user: User = Depends(get_current_user)) -> SimulationResponse:
    """
    Generates synthetic traffic data, predicts congestion using the ML model,
    allocates green-signal timings, and returns the full result set.

    Requires a valid JWT bearer token.
    """
    global simulation_count
    simulation_count += 1

    result = run_simulation()

    # Persist a lightweight log entry
    analysis = result["analysis"]
    add_log(
        {
            "avg_congestion": analysis["avg_congestion"],
            "critical_junction": analysis["critical_junction"],
            "critical_congestion": analysis["critical_congestion"],
            "triggered_by": user.username,
        }
    )

    return SimulationResponse(**result)
