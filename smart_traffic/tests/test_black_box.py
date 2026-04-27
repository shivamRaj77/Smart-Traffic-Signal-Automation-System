"""Black-box tests for API behavior without relying on internal algorithm details."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

import routes.simulate as simulate_route
from db import SessionLocal, init_db
from db_models import SimulationLogORM, SignalOverrideORM, UserORM
from main import app
from services.auth_service import create_default_admin


class TestApiBlackBox(unittest.TestCase):
    """Validate endpoint contracts and access control."""

    def setUp(self) -> None:
        init_db()
        with SessionLocal() as db:
            db.query(SimulationLogORM).delete()
            db.query(SignalOverrideORM).delete()
            db.query(UserORM).delete()
            db.commit()
        simulate_route.simulation_count = 0
        create_default_admin()
        self.client = TestClient(app)

    def _login_and_get_token(self, username: str, password: str) -> str:
        resp = self.client.post(
            "/api/auth/login",
            json={"username": username, "password": password},
        )
        self.assertEqual(resp.status_code, 200)
        return resp.json()["access_token"]

    def test_register_and_login_success(self) -> None:
        register = self.client.post(
            "/api/auth/register",
            json={"username": "alice", "password": "alice123", "role": "user"},
        )
        self.assertEqual(register.status_code, 201)

        login = self.client.post(
            "/api/auth/login",
            json={"username": "alice", "password": "alice123"},
        )
        self.assertEqual(login.status_code, 200)
        self.assertIn("access_token", login.json())

    def test_register_duplicate_username_returns_409(self) -> None:
        self.client.post(
            "/api/auth/register",
            json={"username": "bob", "password": "bobpass1", "role": "user"},
        )
        duplicate = self.client.post(
            "/api/auth/register",
            json={"username": "bob", "password": "bobpass1", "role": "user"},
        )

        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(duplicate.json()["detail"], "Username already taken")

    def test_simulate_requires_authentication(self) -> None:
        resp = self.client.post("/api/simulate")
        self.assertEqual(resp.status_code, 401)

    def test_simulate_with_valid_token_returns_9_junctions(self) -> None:
        token = self._login_and_get_token("admin", "admin123")
        resp = self.client.post(
            "/api/simulate",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("junctions", body)
        self.assertEqual(len(body["junctions"]), 9)
        self.assertIn("analysis", body)

    def test_non_admin_cannot_access_admin_stats(self) -> None:
        self.client.post(
            "/api/auth/register",
            json={"username": "carol", "password": "carol123", "role": "user"},
        )
        token = self._login_and_get_token("carol", "carol123")

        resp = self.client.get(
            "/api/admin/stats",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 403)

    def test_admin_override_reflected_in_next_simulation(self) -> None:
        token = self._login_and_get_token("admin", "admin123")

        ovr_resp = self.client.post(
            "/api/admin/override",
            headers={"Authorization": f"Bearer {token}"},
            json={"junction_id": "J1", "direction": "north", "green_time": 60},
        )
        self.assertEqual(ovr_resp.status_code, 201)

        sim_resp = self.client.post(
            "/api/simulate",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(sim_resp.status_code, 200)

        body = sim_resp.json()
        j1 = next(j for j in body["junctions"] if j["junction_id"] == "J1")
        self.assertEqual(j1["green_times"]["north"], 60)


if __name__ == "__main__":
    unittest.main()
