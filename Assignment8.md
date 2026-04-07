# Assignment 8 - White Box Testing and Black Box Testing

## Objective
Perform:
1. White Box Testing (internal logic aware)
2. Black Box Testing (API behavior without internal implementation assumptions)

Also execute the tests and report results.

## Testing Modules Added (Suitable Locations)
- `smart_traffic/tests/test_white_box.py`
- `smart_traffic/tests/test_black_box.py`

These are placed under the backend module (`smart_traffic`) so they can directly test service logic and API endpoints.

## White Box Test Cases

| ID | Test Type | Target Function/Path | Test Case Description | Expected Result | Actual Result |
|---|---|---|---|---|---|
| WB-01 | White Box | `services.traffic_service.predict_congestion` | Input mixed traffic values for all directions and verify normalization branch. | All values in range [0, 1] and max score is 1.0. | Pass |
| WB-02 | White Box | `services.traffic_service.predict_congestion` | Force model output negative for all directions to hit `max(raw, 0)` and `max_score == 0` fallback branch. | Returned congestion is all 0.0. | Pass |
| WB-03 | White Box | `services.traffic_service.allocate_green_times` | Equal congestion shares without overrides. Validate minimum-time and full-cycle allocation logic. | Every direction >= minimum and total equals base cycle (120s). | Pass |
| WB-04 | White Box | `services.traffic_service.allocate_green_times` | Create admin override for J1 north and test override branch. | Overridden direction green time exactly matches override value. | Pass |
| WB-05 | White Box | `services.traffic_service.run_simulation` | Execute full simulation flow and validate aggregate city output shape. | 9 junctions + valid analysis fields with avg congestion in [0, 1]. | Pass |

## Black Box Test Cases

| ID | Test Type | Endpoint | Test Case Description | Input | Expected Result | Actual Result |
|---|---|---|---|---|---|---|
| BB-01 | Black Box | `POST /api/auth/register` + `POST /api/auth/login` | Register and login with valid credentials. | username/password valid | Register 201, Login 200 with `access_token`. | Pass |
| BB-02 | Black Box | `POST /api/auth/register` | Attempt duplicate registration. | same username twice | 409 Conflict with duplicate message. | Pass |
| BB-03 | Black Box | `POST /api/simulate` | Call protected simulation endpoint without token. | no auth header | 401 Unauthorized. | Pass |
| BB-04 | Black Box | `POST /api/simulate` | Call simulation with valid token and validate contract. | admin bearer token | 200 with `junctions` list of 9 and `analysis` object. | Pass |
| BB-05 | Black Box | `GET /api/admin/stats` | Access admin route with non-admin user token. | user bearer token | 403 Forbidden. | Pass |
| BB-06 | Black Box | `POST /api/admin/override` then `POST /api/simulate` | Set override and verify behavior in next simulation response. | J1 north = 60 | Returned J1 north green time equals 60. | Pass |

## Test Execution
Command used:

```powershell
Set-Location "d:\Smart-Traffic-Signal-Automation-System\smart_traffic"
d:/Smart-Traffic-Signal-Automation-System/.venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py" -v
```

## Execution Result Summary
- Total tests run: 11
- Passed: 11
- Failed: 0
- Errors: 0
- Final status: OK

Note:
- During execution, deprecation warnings were displayed by third-party dependencies (`starlette`, `python-jose`) under Python 3.14, but they did not affect test correctness or pass/fail status.
