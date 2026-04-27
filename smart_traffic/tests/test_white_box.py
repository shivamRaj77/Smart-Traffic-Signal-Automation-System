"""White-box tests for internal traffic simulation logic."""

from __future__ import annotations

import unittest

import numpy as np

from db import SessionLocal, init_db
from db_models import SignalOverrideORM
from models.override import SignalOverride, add_override
from services import traffic_service
from utils.config import BASE_SIGNAL_CYCLE_SECONDS, MIN_GREEN_TIME_SECONDS


class TestTrafficServiceWhiteBox(unittest.TestCase):
    """Validate internal code paths of the traffic service module."""

    def setUp(self) -> None:
        init_db()
        with SessionLocal() as db:
            db.query(SignalOverrideORM).delete()
            db.commit()

    def test_predict_congestion_normalized_scores(self) -> None:
        features = {
            "north": {"vehicle_count": 100, "avg_speed": 10.0},
            "south": {"vehicle_count": 40, "avg_speed": 20.0},
            "east": {"vehicle_count": 20, "avg_speed": 40.0},
            "west": {"vehicle_count": 80, "avg_speed": 8.0},
        }

        result = traffic_service.predict_congestion(features)

        self.assertEqual(set(result.keys()), {"north", "south", "east", "west"})
        self.assertTrue(all(0.0 <= score <= 1.0 for score in result.values()))
        self.assertAlmostEqual(max(result.values()), 1.0, places=4)

    def test_predict_congestion_all_negative_model_outputs_become_zero(self) -> None:
        original_model = traffic_service._model

        class _AlwaysNegativeModel:
            def predict(self, X: np.ndarray) -> np.ndarray:
                return np.array([-5.0])

        traffic_service._model = _AlwaysNegativeModel()  # type: ignore[assignment]
        try:
            features = {
                "north": {"vehicle_count": 50, "avg_speed": 25.0},
                "south": {"vehicle_count": 55, "avg_speed": 30.0},
                "east": {"vehicle_count": 60, "avg_speed": 28.0},
                "west": {"vehicle_count": 45, "avg_speed": 22.0},
            }

            result = traffic_service.predict_congestion(features)
            self.assertEqual(result, {"north": 0.0, "south": 0.0, "east": 0.0, "west": 0.0})
        finally:
            traffic_service._model = original_model

    def test_allocate_green_times_meets_cycle_and_minimum(self) -> None:
        congestion = {"north": 0.25, "south": 0.25, "east": 0.25, "west": 0.25}
        with SessionLocal() as db:
            green = traffic_service.allocate_green_times(congestion, "J1", db)

        self.assertEqual(sum(green.values()), BASE_SIGNAL_CYCLE_SECONDS)
        self.assertTrue(all(sec >= MIN_GREEN_TIME_SECONDS for sec in green.values()))

    def test_allocate_green_times_applies_admin_override(self) -> None:
        with SessionLocal() as db:
            add_override(
                db,
                SignalOverride(
                    junction_id="J1",
                    direction="north",
                    green_time=55,
                    set_by="admin",
                ),
            )
        congestion = {"north": 1.0, "south": 0.1, "east": 0.1, "west": 0.1}

        with SessionLocal() as db:
            green = traffic_service.allocate_green_times(congestion, "J1", db)

        self.assertEqual(green["north"], 55)
        self.assertIn("south", green)
        self.assertIn("east", green)
        self.assertIn("west", green)

    def test_run_simulation_returns_expected_city_structure(self) -> None:
        with SessionLocal() as db:
            payload = traffic_service.run_simulation(db)

        self.assertIn("junctions", payload)
        self.assertIn("analysis", payload)
        self.assertEqual(len(payload["junctions"]), 9)

        analysis = payload["analysis"]
        self.assertIn("critical_junction", analysis)
        self.assertIn("least_congested", analysis)
        self.assertTrue(0.0 <= analysis["avg_congestion"] <= 1.0)


if __name__ == "__main__":
    unittest.main()
