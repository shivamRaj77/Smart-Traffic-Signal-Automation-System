# 🚦 Traffic Signal Control & Optimization System
## Use Cases Specification

---

# 1. Introduction

## 1.1 Purpose
This document describes the functional use cases of the Traffic Signal Control & Optimization System.  
It explains how different actors interact with the system to collect traffic data, control signals, and analyze traffic performance.

## 1.2 Scope
The system:
- Captures real-time traffic data
- Calculates vehicle density
- Optimizes signal timings
- Stores traffic data
- Provides monitoring, analytics, and reports

---

# 2. Actors

| Actor | Description |
|--------|-------------|
| Traffic Administrator | Manages system, views analytics, simulations, and reports |
| Traffic Sensor System | Captures real-time traffic and counts vehicles |
| Signal Controller | Optimizes signal timing and updates traffic lights |
| Database | Stores and retrieves traffic and signal information |

---

# 3. Use Case Summary

| ID | Use Case | Actor |
|-------|---------------------------|-----------------------|
| UC-01 | Capture Traffic Data | Traffic Sensor System |
| UC-02 | Count Vehicles | Traffic Sensor System |
| UC-03 | Send Density Data | Traffic Sensor System |
| UC-04 | Receive Density Data | Signal Controller |
| UC-05 | Select Control Mode | Signal Controller |
| UC-06 | Optimize Signal Timing | Signal Controller |
| UC-07 | Update Traffic Signals | Signal Controller |
| UC-08 | Log Signal Data | System |
| UC-09 | Store Data | Database |
| UC-10 | Retrieve Metrics | Database |
| UC-11 | View Analytics | Traffic Administrator |
| UC-12 | Generate Report | Traffic Administrator |
| UC-13 | Login | Traffic Administrator |
| UC-14 | View Simulation | Traffic Administrator |

---

# 4. Detailed Use Cases

---

## UC-01: Capture Traffic Data
**Actor:** Traffic Sensor System  

### Preconditions
- Sensors are active and connected

### Main Flow
1. Sensor monitors intersection  
2. Detects vehicles  
3. Captures raw traffic data  

### Postconditions
- Traffic data available for counting

---

## UC-02: Count Vehicles
**Actor:** Traffic Sensor System  

### Flow
1. Vehicles detected  
2. Counter increments  
3. Total count calculated  

### Postconditions
- Vehicle count generated

---

## UC-03: Send Density Data
**Actor:** Traffic Sensor System  

### Flow
1. Calculate density using vehicle count  
2. Send density value to controller  

### Postconditions
- Controller receives density data

---

## UC-04: Receive Density Data
**Actor:** Signal Controller  

### Flow
1. Receive data from sensors  
2. Validate data  
3. Forward for optimization  

---

## UC-05: Select Control Mode
**Actor:** Signal Controller  

### Description
Choose signal strategy.

### Options
- Fixed Mode  
- Adaptive Mode  

### Flow
1. Read configuration  
2. Select mode  

---

## UC-06: Optimize Signal Timing
**Actor:** Signal Controller  

### Flow
1. Analyze density  
2. Calculate green/red durations  
3. Create optimized plan  

### Postconditions
- Optimized timings prepared

---

## UC-07: Update Traffic Signals
**Actor:** Signal Controller  

### Flow
1. Apply timing plan  
2. Update traffic lights  
3. Start next signal cycle  

---

## UC-08: Log Signal Data
**Actor:** System  

### Flow
1. Record signal changes  
2. Store timestamps  
3. Save logs  

---

## UC-09: Store Data
**Actor:** Database  

### Flow
1. Receive traffic and signal data  
2. Save records in database tables  

---

## UC-10: Retrieve Metrics
**Actor:** Database  

### Flow
1. Receive analytics request  
2. Fetch historical data  
3. Return results  

---

## UC-11: View Analytics
**Actor:** Traffic Administrator  

### Preconditions
- Administrator logged in

### Flow
1. Open dashboard  
2. Select metrics  
3. View charts and statistics  

---

## UC-12: Generate Report
**Actor:** Traffic Administrator  

### Flow
1. Choose date range  
2. Compile traffic metrics  
3. Generate report (PDF/CSV)  
4. Download/export  

---

## UC-13: Login
**Actor:** Traffic Administrator  

### Flow
1. Enter username and password  
2. Validate credentials  
3. Grant dashboard access  

### Alternate Flow
- Invalid credentials → show error message  

---

## UC-14: View Simulation
**Actor:** Traffic Administrator  

### Flow
1. Select intersection  
2. Run traffic simulation  
3. Observe flow and performance  

---

# 5. Use Case Relationships

## Includes
- Optimize Signal Timing → includes Receive Density Data  
- View Analytics → includes Retrieve Metrics  
- Generate Report → includes Retrieve Metrics  

## Extends
- Adaptive Mode extends Fixed Mode  

---

# 6. Assumptions
- Sensors provide accurate vehicle counts  
- Network connectivity exists  
- Database is available  
- Administrator has valid credentials  

---

# 7. Future Enhancements
- AI-based congestion prediction  
- Emergency vehicle prioritization  
- Multi-intersection coordination  
- Cloud deployment  
- Mobile dashboard  

---
