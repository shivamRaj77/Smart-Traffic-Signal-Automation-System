# Software Requirements Specification (SRS)

## Project: Smart Traffic Signal Automation System  
**Module:** CS331 Software Engineering Lab  
**Group:** 9  

**Members:**
- Shivam Panwar (2301200)  
- Shivam Raj (2301202)  
- Uddhav Tomar (2301235)  

**Version:** 1.0  
**Date:** 27 Jan 2026  

---

## 1. Functional Requirements (FR)

Functional requirements describe what the system must do.

### FR-1: Traffic Data Acquisition & Monitoring
- The system shall collect real-time traffic data for each junction, including vehicle
  count and average speed for all four directions (North, South, East, West).
- The system shall support synthetic traffic data generation for testing and simulation
  purposes.
- The system shall periodically update traffic data at fixed intervals to reflect current
  road conditions.

---

### FR-2: Congestion Detection & Analysis
- The system shall compute congestion levels for each direction of a junction using
  traffic parameters such as vehicle count and speed.
- The system shall classify congestion into predefined levels (Low, Medium, High).
- The system shall maintain congestion data independently for each junction in the
  traffic network.

---

### FR-3: Adaptive Signal Timing Control
- The system shall dynamically calculate green signal duration for each direction based
  on the detected congestion level.
- The system shall ensure a minimum green signal time for all directions to avoid
  starvation.
- The system shall allocate longer green signal durations to directions with higher
  congestion.
- The system shall operate independently for multiple junctions arranged in a grid-based
  road network.

---

### FR-4: Multi-Junction Traffic Coordination
- The system shall support traffic management for multiple interconnected junctions
  (e.g., a 3×3 junction grid).
- The system shall compute congestion statistics separately for each junction.
- The system shall identify the most congested junction within the network at any given
  time.

---

### FR-5: Decision Support & Monitoring Interface
- The system shall display congestion levels and green signal timings for each junction.
- The system shall provide advisory outputs highlighting critical junctions that require
  immediate attention.
- The system shall generate human-readable recommendations such as increasing
  monitoring or traffic diversion for high-congestion junctions.

---

## 2. Non-Functional Requirements (NFR)

Non-functional requirements define how well the system performs.

- **NFR-1 (Performance):**  
  The system shall compute congestion levels and signal timings within a short response
  time suitable for real-time traffic control.

- **NFR-2 (Scalability):**  
  The system architecture shall support easy expansion to additional junctions without
  significant redesign.

- **NFR-3 (Reliability):**  
  The system shall continue to function correctly under fluctuating traffic loads and
  incomplete data inputs.

- **NFR-4 (Usability):**  
  The system shall present traffic and signal information in a clear and understandable
  manner suitable for traffic operators.

- **NFR-5 (Maintainability):**  
  The system shall be modular, allowing independent updates to traffic analysis, signal
  control logic, and monitoring components.

- **NFR-6 (Extensibility):**  
  The system shall allow future integration with real-world sensors, cameras, or smart
  city infrastructure.

---

## 3. Assumptions & Constraints

- The system assumes traffic flows through four-way junctions.
- Real-world deployment would require sensor integration, which is simulated in this
  project.
- The project focuses on logic and automation rather than physical signal hardware
  control.

---

## 4. System Scope

The Smart Traffic Signal Automation System aims to simulate an intelligent and adaptive
traffic management environment for multi-junction road networks. The project focuses on
algorithmic decision-making, congestion analysis, and signal timing optimization rather
than real-world hardware deployment.
