"""
Admin-only routes – user management, stats, logs, signal overrides.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from db import get_db
from models.override import SignalOverride, add_override, get_all_overrides
from models.simulation_log import get_logs
from models.user import User, delete_user_by_id, get_all_users
from schemas.admin import LogEntry, OverrideRequest, OverrideResponse, StatsResponse
from schemas.auth import UserResponse
from services.auth_service import require_admin
from utils.config import DIRECTIONS, JUNCTIONS

router = APIRouter()


# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------

@router.get(
    "/users",
    response_model=list[UserResponse],
    summary="List all registered users (admin only)",
)
async def list_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    """Return every registered user."""
    return [
        UserResponse(id=u.id, username=u.username, role=u.role, created_at=u.created_at)
        for u in get_all_users(db)
    ]


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a user by id (admin only)",
    responses={404: {"description": "User not found"}},
)
async def delete_user(
    user_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Remove a user from the system."""
    if not delete_user_by_id(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": f"User {user_id} deleted"}


# ---------------------------------------------------------------------------
# System stats
# ---------------------------------------------------------------------------

@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Aggregate system statistics (admin only)",
)
async def stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> StatsResponse:
    """Return high-level system counters."""
    from routes.simulate import simulation_count  # avoid circular at module level

    users = get_all_users(db)
    return StatsResponse(
        total_users=len(users),
        total_admins=sum(1 for u in users if u.role == "admin"),
        total_simulations=simulation_count,
        total_overrides=len(get_all_overrides(db)),
    )


# ---------------------------------------------------------------------------
# Simulation logs
# ---------------------------------------------------------------------------

@router.get(
    "/logs",
    response_model=list[LogEntry],
    summary="Recent simulation logs (admin only)",
)
async def logs(
    limit: int = Query(default=50, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[LogEntry]:
    """Return the most recent simulation log entries."""
    raw = get_logs(db, limit)
    return [
        LogEntry(
            timestamp=entry["timestamp"],
            avg_congestion=entry["avg_congestion"],
            critical_junction=entry["critical_junction"],
            critical_congestion=entry["critical_congestion"],
        )
        for entry in raw
    ]


# ---------------------------------------------------------------------------
# Signal overrides
# ---------------------------------------------------------------------------

@router.post(
    "/override",
    response_model=OverrideResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Manually set green signal time for a junction direction",
)
async def create_override(
    body: OverrideRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> OverrideResponse:
    """
    Admin sets a manual green-signal duration for a specific junction + direction.
    This override will be applied in subsequent simulations.
    """
    if body.junction_id not in JUNCTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid junction_id. Must be one of {JUNCTIONS}",
        )
    if body.direction not in DIRECTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid direction. Must be one of {DIRECTIONS}",
        )

    override = add_override(
        db,
        SignalOverride(
            junction_id=body.junction_id,
            direction=body.direction,
            green_time=body.green_time,
            set_by=admin.username,
        )
    )
    return OverrideResponse(
        id=override.id,
        junction_id=override.junction_id,
        direction=override.direction,
        green_time=override.green_time,
        set_by=override.set_by,
        created_at=override.created_at,
    )


@router.get(
    "/overrides",
    response_model=list[OverrideResponse],
    summary="List all active signal overrides (admin only)",
)
async def list_overrides(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[OverrideResponse]:
    """Return every active admin override."""
    return [
        OverrideResponse(
            id=o.id,
            junction_id=o.junction_id,
            direction=o.direction,
            green_time=o.green_time,
            set_by=o.set_by,
            created_at=o.created_at,
        )
        for o in get_all_overrides(db)
    ]
