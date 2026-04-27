"""
Model information endpoint – exposes metadata about the ML prediction layer.
"""

from __future__ import annotations

from fastapi import APIRouter

from services.traffic_service import MODEL_INFO

router = APIRouter()


@router.get(
    "/info",
    summary="Return metadata about the congestion prediction model",
    response_model=dict[str, str],
)
async def model_info() -> dict[str, str]:
    """
    Public endpoint that describes the ML model used for congestion
    prediction, including model type, features, and version.
    """
    return MODEL_INFO
