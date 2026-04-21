"""
Traffic simulation engine.

1. Generates synthetic per-direction traffic data for each junction.
2. Predicts congestion via a lightweight sklearn model (DummyRegressor
   augmented with a rule-based formula so results are meaningful).
3. Allocates green-signal time proportionally to congestion share.
"""

from __future__ import annotations

import random
from typing import Any

import numpy as np
from sklearn.linear_model import Ridge
from sqlalchemy.orm import Session

from models.override import get_override
from utils.config import (
    BASE_SIGNAL_CYCLE_SECONDS,
    DIRECTIONS,
    JUNCTIONS,
    MIN_GREEN_TIME_SECONDS,
)

# ---------------------------------------------------------------------------
# Lightweight ML model – trained once at import time on synthetic data
# ---------------------------------------------------------------------------
_CONGESTION_EPS = 1.0  # small constant to avoid division by zero


def _train_model() -> Ridge:
    """
    Train a Ridge regression model on synthetic traffic features.

    Features per sample: [vehicle_count, avg_speed]
    Target: congestion = vehicle_count / (avg_speed + EPS)
    The model learns this mapping so we can call `predict_congestion` later.
    """
    rng = np.random.RandomState(42)
    n_samples = 2000
    vehicle_counts = rng.randint(5, 120, size=n_samples).astype(float)
    avg_speeds = rng.uniform(5.0, 60.0, size=n_samples)
    targets = vehicle_counts / (avg_speeds + _CONGESTION_EPS)

    X = np.column_stack([vehicle_counts, avg_speeds])
    model = Ridge(alpha=1.0)
    model.fit(X, targets)
    return model


_model: Ridge = _train_model()

MODEL_INFO: dict[str, str] = {
    "model_type": "Ridge Regression (sklearn)",
    "features": "vehicle_count, avg_speed",
    "target": "congestion = vehicle_count / (avg_speed + 1.0)",
    "version": "1.0.0",
    "training_samples": "2000 synthetic samples",
}


# ---------------------------------------------------------------------------
# Data generation
# ---------------------------------------------------------------------------

def _generate_direction_data() -> dict[str, Any]:
    """Generate realistic traffic readings for a single direction."""
    vehicle_count = random.randint(5, 110)
    avg_speed = round(random.uniform(5.0, 60.0), 1)
    return {"vehicle_count": vehicle_count, "avg_speed": avg_speed}


def _generate_junction_traffic() -> dict[str, dict[str, Any]]:
    """Generate traffic data for all four directions of a junction."""
    return {d: _generate_direction_data() for d in DIRECTIONS}


# ---------------------------------------------------------------------------
# Congestion prediction
# ---------------------------------------------------------------------------

def predict_congestion(features: dict[str, dict[str, Any]]) -> dict[str, float]:
    """
    Predict normalised congestion (0–1) for each direction using the trained
    Ridge model.

    Parameters
    ----------
    features : dict mapping direction → {"vehicle_count": int, "avg_speed": float}

    Returns
    -------
    dict mapping direction → congestion score ∈ [0, 1]
    """
    raw_scores: dict[str, float] = {}
    for direction, data in features.items():
        X = np.array([[data["vehicle_count"], data["avg_speed"]]])
        raw = float(_model.predict(X)[0])
        raw_scores[direction] = max(raw, 0.0)

    # Normalise to [0, 1] across the four directions
    max_score = max(raw_scores.values()) if raw_scores else 1.0
    if max_score == 0:
        max_score = 1.0
    return {d: round(min(v / max_score, 1.0), 4) for d, v in raw_scores.items()}


# ---------------------------------------------------------------------------
# Signal timing allocation
# ---------------------------------------------------------------------------

def allocate_green_times(
    congestion: dict[str, float],
    junction_id: str,
    db: Session,
) -> dict[str, int]:
    """
    Distribute *BASE_SIGNAL_CYCLE_SECONDS* among four directions proportionally
    to their congestion share.  Admin overrides are applied when present.

    Every direction gets at least *MIN_GREEN_TIME_SECONDS*.
    """
    total_congestion = sum(congestion.values()) or 1.0
    remaining_cycle = BASE_SIGNAL_CYCLE_SECONDS - (MIN_GREEN_TIME_SECONDS * len(DIRECTIONS))
    if remaining_cycle < 0:
        remaining_cycle = 0

    green_times: dict[str, int] = {}
    for direction in DIRECTIONS:
        ovr = get_override(db, junction_id, direction)
        if ovr is not None:
            green_times[direction] = ovr.green_time
        else:
            share = congestion.get(direction, 0.0) / total_congestion
            green_times[direction] = MIN_GREEN_TIME_SECONDS + int(
                round(share * remaining_cycle)
            )
    return green_times


# ---------------------------------------------------------------------------
# Full simulation run
# ---------------------------------------------------------------------------

def run_simulation(db: Session) -> dict[str, Any]:
    """
    Execute one full simulation tick for all 9 junctions.

    Returns the payload expected by the ``/api/simulate`` endpoint.
    """
    junction_results: list[dict[str, Any]] = []

    for jid in JUNCTIONS:
        traffic = _generate_junction_traffic()
        congestion = predict_congestion(traffic)
        green_times = allocate_green_times(congestion, jid, db)
        total_cong = round(sum(congestion.values()) / len(DIRECTIONS), 4)

        junction_results.append(
            {
                "junction_id": jid,
                "traffic": traffic,
                "congestion": congestion,
                "green_times": green_times,
                "total_congestion": total_cong,
            }
        )

    # --- analysis summary ---
    cong_vals = [(j["junction_id"], j["total_congestion"]) for j in junction_results]
    avg_cong = round(sum(v for _, v in cong_vals) / len(cong_vals), 4)
    critical = max(cong_vals, key=lambda x: x[1])
    least = min(cong_vals, key=lambda x: x[1])

    analysis = {
        "avg_congestion": avg_cong,
        "critical_junction": critical[0],
        "critical_congestion": critical[1],
        "least_congested": least[0],
        "least_congestion": least[1],
    }

    return {"junctions": junction_results, "analysis": analysis}
