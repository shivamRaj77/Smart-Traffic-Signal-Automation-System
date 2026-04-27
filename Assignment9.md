# Assignment 9: Test Plan, Test Execution, and Defect Analysis

## Q1(a) Test Plan

### 1. Objective of Testing
The objective is to verify that the Access Control and Simulation Control module works correctly, securely, and consistently. Testing focuses on:
- Correct authentication and authorization behavior
- Correct access restrictions for protected and admin-only endpoints
- Correct handling of override-driven traffic signal control constraints

### 2. Scope (Modules and Features to be Tested)
In scope:
- Authentication APIs:
  - `POST /api/auth/register`
  - `POST /api/auth/login`
- Protected simulation API:
  - `POST /api/simulate`
- Admin APIs:
  - `GET /api/admin/stats`
  - `GET /api/admin/users`
  - `DELETE /api/admin/users/{user_id}`
  - `POST /api/admin/override`

Out of scope:
- Frontend UI rendering and styling
- Performance/load testing
- External database engines (tests executed on local SQLite setup)

### 3. Types of Testing Performed
- Unit-level API contract verification via deterministic API calls
- Integration testing across auth, admin, and simulation routes
- System behavior validation for role-based access control and signal constraints
- Negative testing for invalid/unsafe scenarios

### 4. Tools Used
- Python 3.14 virtual environment
- FastAPI TestClient
- Existing project backend and SQLAlchemy models
- Custom execution script:
  - `smart_traffic/tests/assignment9_test_runner.py`
- Evidence log output file:
  - `smart_traffic/tests/assignment9_execution_log_utf8.txt`

### 5. Entry Criteria
- Backend dependencies installed from `smart_traffic/requirements.txt`
- Database initialization available (`init_db`)
- Default admin bootstrap available (`create_default_admin`)
- APIs and schemas compile without runtime import errors

### 6. Exit Criteria
- At least 8 designed test cases executed end-to-end
- Actual outputs recorded for every test case
- Pass/Fail status assigned for every test case
- Minimum 3 defects identified, reproduced, and documented with severity and suggested fixes

---

## Q1(b) Designed Test Cases for One Major Module

### Selected Major Module
Access Control and Simulation Control module (authentication, authorization, admin control, and override-driven simulation behavior).

### Test Case Design and Execution Results

| Test Case ID | Test Scenario / Description | Input Data | Expected Output | Actual Output | Status |
|---|---|---|---|---|---|
| A9-TC-01 | Register with valid user credentials | `{"username":"alice","password":"alice123","role":"user"}` | HTTP 201 with created user details | `status=201, role=user` | Pass |
| A9-TC-02 | Register duplicate username | Register `alice` twice | Second request HTTP 409 with duplicate message | `status=409, detail=Username already taken` | Pass |
| A9-TC-03 | Login with valid credentials | `{"username":"alice","password":"alice123"}` | HTTP 200 with non-empty access token | `status=200, has_access_token=True` | Pass |
| A9-TC-04 | Login with invalid password | `{"username":"alice","password":"wrong-pass"}` | HTTP 401 invalid credentials | `status=401, detail=Invalid username or password` | Pass |
| A9-TC-05 | Run simulation without authentication | `POST /api/simulate` without bearer token | HTTP 401 unauthorized | `status=401, detail=Not authenticated` | Pass |
| A9-TC-06 | Access admin stats with non-admin account | Login as `user`, call `GET /api/admin/stats` | HTTP 403 forbidden | `status=403, detail=Admin privileges required` | Pass |
| A9-TC-07 | Prevent public admin-role registration | `{"username":"eve","password":"eve12345","role":"admin"}` | Request rejected (4xx), no unauthorized admin creation | `status=201, role=admin created` | Fail |
| A9-TC-08 | Prevent authenticated admin from deleting own account | Login as admin, delete own user id | Deletion blocked (4xx) to avoid lockout | `delete_status=200; followup admin request returned 401 User not found` | Fail |
| A9-TC-09 | Ensure override does not violate total cycle limit | Set `J1 north=120`, run simulation | Total J1 cycle <= 120 seconds | `J1 total_cycle=230` | Fail |

---

## Q2(a) Test Case Execution and Evidence

### Execution Command
Run from `smart_traffic` directory:

```powershell
d:/Smart-Traffic-Signal-Automation-System/.venv/Scripts/python.exe tests/assignment9_test_runner.py > tests/assignment9_execution_log_utf8.txt
```

### Execution Summary
- Total test cases executed: 9
- Passed: 6
- Failed: 3

### Evidence (Logs)
- Full execution log:
  - `smart_traffic/tests/assignment9_execution_log_utf8.txt`
- Execution script used:
  - `smart_traffic/tests/assignment9_test_runner.py`

---

## Q2(b) Defect Identification and Analysis

### Bug ID: A9-BUG-01
- Description:
  Public registration endpoint allows users to self-assign `admin` role.
- Steps to Reproduce:
  1. Call `POST /api/auth/register`.
  2. Send payload with `role` set to `admin`.
- Expected Result:
  Request should be rejected (for example 403/422), or role should be forced to `user`.
- Actual Result:
  Endpoint returns HTTP 201 and creates an admin account.
- Severity:
  High
- Suggested Fix:
  Remove `role` from public registration payload or force role to `user` on backend. Admin creation should be restricted to protected admin-only workflows.

### Bug ID: A9-BUG-02
- Description:
  Admin user can delete own account via admin delete API, causing administrative lockout.
- Steps to Reproduce:
  1. Login as default admin.
  2. Fetch own id from `GET /api/admin/users`.
  3. Call `DELETE /api/admin/users/{admin_id}`.
  4. Call any admin endpoint using same token.
- Expected Result:
  Self-delete should be blocked (4xx), and system should preserve at least one valid admin account.
- Actual Result:
  Delete returns HTTP 200; next admin request returns HTTP 401 (`User not found`).
- Severity:
  High
- Suggested Fix:
  Add guard in delete-user route:
  - Prevent deleting currently authenticated user.
  - Prevent deletion if target is the last admin in system.

### Bug ID: A9-BUG-03
- Description:
  Applying high override value can violate total junction signal cycle constraint.
- Steps to Reproduce:
  1. Login as admin.
  2. Set override `J1 north = 120` via `POST /api/admin/override`.
  3. Run `POST /api/simulate`.
  4. Sum `green_times` for J1.
- Expected Result:
  Total allocated green time should not exceed `BASE_SIGNAL_CYCLE_SECONDS` (120s).
- Actual Result:
  Total cycle becomes 230 seconds for J1.
- Severity:
  Medium
- Suggested Fix:
  Update allocation logic to normalize final cycle after overrides. If overrides exceed available cycle, either:
  - Reject invalid override values dynamically based on current cycle policy, or
  - Rebalance remaining directions while strictly enforcing total cycle cap.

---

## Final Observation
The module passes core positive and access-control behavior checks, but three significant defects were found in security and signal-allocation constraint handling. These should be fixed before production deployment.

---

## Completion Checklist

- **Q1(a) Test Plan:** Completed and documented in this file.
- **Q1(b) Test Cases:** Completed — 9 test cases designed (≥8 required) and listed above.
- **Q2(a) Test Execution:** Completed — tests executed and evidence saved to [smart_traffic/tests/assignment9_execution_log_utf8.txt](smart_traffic/tests/assignment9_execution_log_utf8.txt).
- **Q2(b) Defect Analysis:** Completed — three defects identified and documented in the "Defect Identification and Analysis" section.

Results:

- Test runner: [smart_traffic/tests/assignment9_test_runner.py](smart_traffic/tests/assignment9_test_runner.py)
- Execution log: [smart_traffic/tests/assignment9_execution_log_utf8.txt](smart_traffic/tests/assignment9_execution_log_utf8.txt)
