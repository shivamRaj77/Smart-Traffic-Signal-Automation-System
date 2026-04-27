"""Assignment 9 test execution runner.

Runs black-box API test scenarios for a major module and prints
structured results that can be used in the assignment report.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Callable

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import routes.simulate as simulate_route
from db import SessionLocal, init_db
from db_models import SimulationLogORM, SignalOverrideORM, UserORM
from main import app
from services.auth_service import create_default_admin
from utils.config import BASE_SIGNAL_CYCLE_SECONDS


@dataclass
class TestResult:
    case_id: str
    description: str
    input_data: str
    expected_output: str
    actual_output: str
    status: str


def reset_state() -> None:
    """Reset persistent test state and recreate default admin user."""
    init_db()
    with SessionLocal() as db:
        db.query(SimulationLogORM).delete()
        db.query(SignalOverrideORM).delete()
        db.query(UserORM).delete()
        db.commit()
    simulate_route.simulation_count = 0
    create_default_admin()


def login_and_get_token(client: TestClient, username: str, password: str) -> str:
    """Authenticate and return bearer token."""
    resp = client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )
    if resp.status_code != 200:
        return ""
    return resp.json().get("access_token", "")


def run_case(
    case_id: str,
    description: str,
    input_data: str,
    expected_output: str,
    fn: Callable[[TestClient], tuple[bool, str]],
) -> TestResult:
    """Execute a single test case and return a structured result."""
    reset_state()
    client = TestClient(app)
    passed, actual = fn(client)
    return TestResult(
        case_id=case_id,
        description=description,
        input_data=input_data,
        expected_output=expected_output,
        actual_output=actual,
        status="Pass" if passed else "Fail",
    )


def execute_assignment9_cases() -> list[TestResult]:
    """Run all Assignment 9 test cases for the selected major module."""
    results: list[TestResult] = []

    results.append(
        run_case(
            "A9-TC-01",
            "Register with valid user credentials",
            '{"username":"alice","password":"alice123","role":"user"}',
            "HTTP 201 with created user details",
            lambda client: (
                (resp := client.post(
                    "/api/auth/register",
                    json={"username": "alice", "password": "alice123", "role": "user"},
                )).status_code
                == 201,
                f"status={resp.status_code}, body={resp.json()}",
            ),
        )
    )

    def tc_02(client: TestClient) -> tuple[bool, str]:
        client.post(
            "/api/auth/register",
            json={"username": "alice", "password": "alice123", "role": "user"},
        )
        dup = client.post(
            "/api/auth/register",
            json={"username": "alice", "password": "alice123", "role": "user"},
        )
        ok = dup.status_code == 409 and dup.json().get("detail") == "Username already taken"
        return ok, f"status={dup.status_code}, body={dup.json()}"

    results.append(
        run_case(
            "A9-TC-02",
            "Register duplicate username",
            "Register alice twice",
            "Second request HTTP 409 with duplicate message",
            tc_02,
        )
    )

    def tc_03(client: TestClient) -> tuple[bool, str]:
        client.post(
            "/api/auth/register",
            json={"username": "alice", "password": "alice123", "role": "user"},
        )
        login = client.post(
            "/api/auth/login",
            json={"username": "alice", "password": "alice123"},
        )
        token = login.json().get("access_token") if login.status_code == 200 else None
        ok = login.status_code == 200 and bool(token)
        return ok, f"status={login.status_code}, has_access_token={bool(token)}"

    results.append(
        run_case(
            "A9-TC-03",
            "Login with valid credentials",
            '{"username":"alice","password":"alice123"}',
            "HTTP 200 with non-empty access_token",
            tc_03,
        )
    )

    def tc_04(client: TestClient) -> tuple[bool, str]:
        client.post(
            "/api/auth/register",
            json={"username": "alice", "password": "alice123", "role": "user"},
        )
        login = client.post(
            "/api/auth/login",
            json={"username": "alice", "password": "wrong-pass"},
        )
        ok = login.status_code == 401
        return ok, f"status={login.status_code}, body={login.json()}"

    results.append(
        run_case(
            "A9-TC-04",
            "Login with invalid password",
            '{"username":"alice","password":"wrong-pass"}',
            "HTTP 401 Invalid credentials",
            tc_04,
        )
    )

    def tc_05(client: TestClient) -> tuple[bool, str]:
        resp = client.post("/api/simulate")
        ok = resp.status_code == 401
        return ok, f"status={resp.status_code}, body={resp.json()}"

    results.append(
        run_case(
            "A9-TC-05",
            "Run simulation without authentication",
            "POST /api/simulate without bearer token",
            "HTTP 401 Unauthorized",
            tc_05,
        )
    )

    def tc_06(client: TestClient) -> tuple[bool, str]:
        client.post(
            "/api/auth/register",
            json={"username": "carol", "password": "carol123", "role": "user"},
        )
        token = login_and_get_token(client, "carol", "carol123")
        resp = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {token}"})
        ok = resp.status_code == 403
        return ok, f"status={resp.status_code}, body={resp.json()}"

    results.append(
        run_case(
            "A9-TC-06",
            "Access admin stats using non-admin token",
            "Login as user then GET /api/admin/stats",
            "HTTP 403 Forbidden",
            tc_06,
        )
    )

    def tc_07(client: TestClient) -> tuple[bool, str]:
        resp = client.post(
            "/api/auth/register",
            json={"username": "eve", "password": "eve12345", "role": "admin"},
        )
        ok = resp.status_code in {400, 403, 422}
        return ok, f"status={resp.status_code}, body={resp.json()}"

    results.append(
        run_case(
            "A9-TC-07",
            "Prevent public admin role registration",
            '{"username":"eve","password":"eve12345","role":"admin"}',
            "Request rejected (HTTP 4xx), no new admin account",
            tc_07,
        )
    )

    def tc_08(client: TestClient) -> tuple[bool, str]:
        token = login_and_get_token(client, "admin", "admin123")
        users = client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
        if users.status_code != 200:
            return False, f"list_users status={users.status_code}, body={users.json()}"

        admin_user = next((u for u in users.json() if u.get("username") == "admin"), None)
        if admin_user is None:
            return False, "admin user not found"

        delete_resp = client.delete(
            f"/api/admin/users/{admin_user['id']}",
            headers={"Authorization": f"Bearer {token}"},
        )
        follow_up = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {token}"})

        ok = delete_resp.status_code in {400, 403}
        return (
            ok,
            "delete_status="
            f"{delete_resp.status_code}, delete_body={delete_resp.json()}, "
            f"followup_stats_status={follow_up.status_code}, followup_stats_body={follow_up.json()}",
        )

    results.append(
        run_case(
            "A9-TC-08",
            "Prevent deletion of currently authenticated admin account",
            "Login as admin, call DELETE /api/admin/users/{admin_id}",
            "Deletion blocked (HTTP 4xx) to avoid admin lockout",
            tc_08,
        )
    )

    def tc_09(client: TestClient) -> tuple[bool, str]:
        token = login_and_get_token(client, "admin", "admin123")
        ovr = client.post(
            "/api/admin/override",
            headers={"Authorization": f"Bearer {token}"},
            json={"junction_id": "J1", "direction": "north", "green_time": 120},
        )
        if ovr.status_code != 201:
            return False, f"override status={ovr.status_code}, body={ovr.json()}"

        sim = client.post(
            "/api/simulate",
            headers={"Authorization": f"Bearer {token}"},
        )
        if sim.status_code != 200:
            return False, f"simulate status={sim.status_code}, body={sim.json()}"

        j1 = next((j for j in sim.json()["junctions"] if j["junction_id"] == "J1"), None)
        if j1 is None:
            return False, "junction J1 not present in simulation output"

        total_cycle = sum(j1["green_times"].values())
        ok = total_cycle <= BASE_SIGNAL_CYCLE_SECONDS
        return ok, f"J1 green_times={j1['green_times']}, total_cycle={total_cycle}"

    results.append(
        run_case(
            "A9-TC-09",
            "Keep signal cycle within base limit when override is applied",
            "Set J1 north override to 120 then run simulation",
            f"Total J1 green cycle <= {BASE_SIGNAL_CYCLE_SECONDS} seconds",
            tc_09,
        )
    )

    return results


def print_report(results: list[TestResult]) -> None:
    """Print a clean execution report."""
    print("ASSIGNMENT 9 TEST EXECUTION REPORT")
    print("=" * 80)
    for r in results:
        print(f"{r.case_id} | {r.status}")
        print(f"Scenario: {r.description}")
        print(f"Input: {r.input_data}")
        print(f"Expected: {r.expected_output}")
        print(f"Actual: {r.actual_output}")
        print("-" * 80)

    total = len(results)
    passed = sum(1 for r in results if r.status == "Pass")
    failed = total - passed
    print(f"TOTAL={total} PASSED={passed} FAILED={failed}")


if __name__ == "__main__":
    print_report(execute_assignment9_cases())