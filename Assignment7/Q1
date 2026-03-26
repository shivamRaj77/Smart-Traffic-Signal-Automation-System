# Assignment Q1: Business Logic Layer (BLL) Modules and UI Interaction

## 1. Introduction

The Smart Traffic Signal Automation System follows a layered architecture:

- Presentation Layer: React frontend pages and components
- API Layer: FastAPI route handlers
- Business Logic Layer (BLL): Service modules implementing domain rules
- Data Layer: In-memory model stores and logs

For this question, the core BLL modules are identified below and their interaction with the already implemented UI is clearly shown.

---

## 2. Core Functional Modules in the Business Logic Layer

### Module A: Authentication and Authorization Logic

Purpose:
- Authenticate users
- Issue and validate JWT tokens
- Enforce role-based access (admin or user)

Implemented in:
- [smart_traffic/services/auth_service.py](smart_traffic/services/auth_service.py)

Business rules implemented:
- Password hashing and verification
- Access token generation with expiry
- Token decoding and subject validation
- Admin privilege enforcement
- Default admin account bootstrap on startup

Presentation layer interaction:
- Login page sends credentials to API:
  - [traffic_frontend/src/pages/LoginPage.jsx](traffic_frontend/src/pages/LoginPage.jsx)
  - API route: [smart_traffic/routes/auth.py](smart_traffic/routes/auth.py)
- Registration page creates account:
  - [traffic_frontend/src/pages/RegisterPage.jsx](traffic_frontend/src/pages/RegisterPage.jsx)
- Frontend stores token and decodes role for route protection:
  - [traffic_frontend/src/context/AuthContext.jsx](traffic_frontend/src/context/AuthContext.jsx)
  - [traffic_frontend/src/App.jsx](traffic_frontend/src/App.jsx)

---

### Module B: Congestion Analysis and Prediction Logic

Purpose:
- Generate traffic features per junction and direction
- Predict congestion score from vehicle count and average speed
- Normalize congestion values for decision making

Implemented in:
- [smart_traffic/services/traffic_service.py](smart_traffic/services/traffic_service.py)

Business rules implemented:
- Synthetic traffic data generation for each direction
- ML-based congestion prediction using Ridge regression
- Normalized congestion values in range 0 to 1

Presentation layer interaction:
- Dashboard Run Simulation action:
  - [traffic_frontend/src/pages/DashboardPage.jsx](traffic_frontend/src/pages/DashboardPage.jsx)
- Detailed Simulation page Run Simulation action:
  - [traffic_frontend/src/pages/SimulationPage.jsx](traffic_frontend/src/pages/SimulationPage.jsx)
- API endpoint handling simulation request:
  - [smart_traffic/routes/simulate.py](smart_traffic/routes/simulate.py)

---

### Module C: Signal Timing Allocation and Override Logic

Purpose:
- Allocate green signal durations dynamically based on congestion
- Respect minimum signal timing constraints
- Apply admin overrides when configured

Implemented in:
- [smart_traffic/services/traffic_service.py](smart_traffic/services/traffic_service.py)
- Override model support:
  - [smart_traffic/models/override.py](smart_traffic/models/override.py)

Business rules implemented:
- Proportional green time distribution across four directions
- Minimum green time per direction
- Manual override priority over computed value

Presentation layer interaction:
- Override creation and listing UI:
  - [traffic_frontend/src/pages/OverridesPage.jsx](traffic_frontend/src/pages/OverridesPage.jsx)
- API routes for overrides:
  - [smart_traffic/routes/admin.py](smart_traffic/routes/admin.py)
- Updated timing values reflected in Dashboard and Simulation pages after next run

---

### Module D: Monitoring, Logging, and Administrative Control Logic

Purpose:
- Produce system-level simulation analytics
- Persist and fetch simulation logs
- Support user management and system statistics for admins

Implemented in:
- Simulation analysis and summary generation:
  - [smart_traffic/services/traffic_service.py](smart_traffic/services/traffic_service.py)
- Log write on each simulation run:
  - [smart_traffic/routes/simulate.py](smart_traffic/routes/simulate.py)
- Admin routes for logs, users, stats, overrides:
  - [smart_traffic/routes/admin.py](smart_traffic/routes/admin.py)

Business rules implemented:
- Average congestion calculation
- Critical and least congested junction identification
- Simulation counter and log retrieval limits
- Admin-only access control for sensitive operations

Presentation layer interaction:
- Logs page:
  - [traffic_frontend/src/pages/LogsPage.jsx](traffic_frontend/src/pages/LogsPage.jsx)
- Users page:
  - [traffic_frontend/src/pages/UsersPage.jsx](traffic_frontend/src/pages/UsersPage.jsx)
- Admin navigation visibility based on role:
  - [traffic_frontend/src/components/Sidebar.jsx](traffic_frontend/src/components/Sidebar.jsx)

---

## 3. End-to-End Interaction Between Presentation Layer and BLL

### Flow 1: Run Simulation

1. User clicks Run Simulation in Dashboard or Simulation page.
2. Frontend sends POST request using API client:
   - [traffic_frontend/src/lib/api.js](traffic_frontend/src/lib/api.js)
3. Request reaches simulation route:
   - [smart_traffic/routes/simulate.py](smart_traffic/routes/simulate.py)
4. Route invokes BLL service run_simulation:
   - [smart_traffic/services/traffic_service.py](smart_traffic/services/traffic_service.py)
5. BLL performs:
   - Data generation
   - Congestion prediction
   - Signal timing allocation
   - City-level analysis
6. Response is rendered in UI cards, charts, and detailed tables:
   - [traffic_frontend/src/pages/DashboardPage.jsx](traffic_frontend/src/pages/DashboardPage.jsx)
   - [traffic_frontend/src/pages/SimulationPage.jsx](traffic_frontend/src/pages/SimulationPage.jsx)

### Flow 2: Admin Override Management

1. Admin submits override form in Overrides page.
2. Frontend calls admin override endpoint.
3. Admin route validates junction and direction.
4. Override is stored and later applied by BLL during signal allocation.
5. New timing is visible after the next simulation response.

### Flow 3: Authentication and Protected Access

1. User logs in from Login page.
2. Backend validates credentials and returns JWT token.
3. Frontend stores token and attaches it to future requests.
4. Protected routes and admin-only screens are conditionally accessible.

---

## 4. Conclusion

The Business Logic Layer of this system is fully implemented through dedicated service modules and route-level orchestration. The core BLL modules are:

- Authentication and Authorization
- Congestion Analysis and Prediction
- Signal Timing Allocation and Overrides
- Monitoring, Logging, and Admin Control

These modules are actively integrated with the existing presentation layer pages, proving clear interaction between UI components and business logic according to layered architecture principles.
