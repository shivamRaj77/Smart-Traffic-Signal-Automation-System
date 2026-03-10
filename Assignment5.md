## Project: Smart Traffic Signal Automation System

---

# I. Hosting of Application Components

## Host Site

Application components are deployed as follows:

* **Frontend (Traffic Monitoring Dashboard)**

  * Hosted on: Web Server (Node.js / Flask)
  * Purpose: Interface for Traffic Administrator to view analytics and reports.

* **Backend Application Logic**

  * Hosted on: Cloud VM / Application Server
  * Example Platforms:

    * AWS EC2
    * Google Cloud Compute Engine
    * Local Server (for simulation)

* **Database**

  * Hosted on: Database Server
  * Example Technologies:

    * PostgreSQL
    * MySQL
    * MongoDB

* **Traffic Sensor Simulation Module**

  * Hosted on: Application Server
  * Purpose: Generate traffic data for simulation.

---

## Deployment Strategy

Deployment steps:

1. **Server Setup**

   * Configure Linux server (Ubuntu)
   * Install runtime environments:

     * Python
     * Node.js
     * Database server

2. **Backend Deployment**

   * Deploy traffic management APIs
   * APIs manage:

     * Traffic data ingestion
     * Congestion analysis
     * Signal optimization

3. **Database Configuration**

   * Create database schema
   * Tables for:

     * Traffic data
     * Signal logs
     * Analytics reports

4. **API Communication**

   * REST APIs used for communication between components
   * Example endpoints:

     * `/traffic-data`
     * `/analyze-congestion`
     * `/update-signal`

5. **Frontend Deployment**

   * Deploy dashboard UI
   * Connect frontend to backend APIs

---

## Security Measures

Basic security measures include:

* HTTPS encryption for API communication
* Firewall rules restricting database access
* Authentication for Traffic Administrator login
* Input validation for traffic data

---

# II. End User Access to Services

End users access the system through a web dashboard.

### Access Flow

* Traffic Administrator logs into the dashboard
* Dashboard sends requests to backend APIs
* Backend processes traffic data
* Database stores traffic and signal data
* Results are returned to dashboard

---

## System Interaction Diagram

```
Traffic Administrator
        │
        ▼
Web Browser
        │
        ▼
+-----------------------+
|   Frontend Dashboard  |
+-----------------------+
        │ REST API
        ▼
+-----------------------+
| Backend Application   |
| Traffic Management    |
+-----------------------+
        │
        ├──► Congestion Analyzer
        │
        ├──► Signal Controller
        │
        ▼
+-----------------------+
| Database Server       |
| Traffic Data Storage  |
+-----------------------+
        ▲
        │
+-----------------------+
| Traffic Sensor Module |
| (Simulation / IoT)    |
+-----------------------+
```

---

# III. Implementation of Application Components

## Component 1: Congestion Analyzer

Purpose:

* Determines traffic congestion level based on vehicle density.

```python
import random
import time
from datetime import datetime

class CongestionAnalyzer:

    def __init__(self):
        self.history = []

    def analyze_congestion(self, vehicle_count, avg_speed):

        if avg_speed <= 0:
            return "Invalid"

        density = vehicle_count / avg_speed

        if density > 1.5:
            congestion = "High"
        elif density > 0.8:
            congestion = "Medium"
        else:
            congestion = "Low"

        timestamp = datetime.now().strftime("%H:%M:%S")

        record = {
            "time": timestamp,
            "vehicles": vehicle_count,
            "speed": avg_speed,
            "density": round(density,2),
            "congestion": congestion
        }

        self.history.append(record)

        print("\n----- Traffic Sensor Reading -----")
        print("Time:", timestamp)
        print("Vehicle Count:", vehicle_count)
        print("Average Speed:", avg_speed)
        print("Density:", round(density,2))
        print("Congestion Level:", congestion)

        return congestion


def simulate_traffic(analyzer):

    while True:
        vehicle_count = random.randint(20,150)
        avg_speed = random.randint(10,80)

        analyzer.analyze_congestion(vehicle_count, avg_speed)

        time.sleep(3)   # simulate sensor update every 3 seconds


analyzer = CongestionAnalyzer()

simulate_traffic(analyzer)
```

---

## Component 2: Signal Controller

Purpose:

* Adjusts traffic signal timing based on congestion level.

```python
import time
import random

class SignalController:

    def __init__(self):
        self.current_signal = "RED"

    def compute_signal_timing(self, congestion):

        if congestion == "High":
            return 60
        elif congestion == "Medium":
            return 40
        else:
            return 20

    def run_signal_cycle(self, congestion):

        green_time = self.compute_signal_timing(congestion)

        print("\n===== Traffic Signal Update =====")
        print("Congestion Level:", congestion)

        self.current_signal = "GREEN"
        print("Signal:", self.current_signal)

        for i in range(green_time,0,-10):
            print("Remaining green time:", i, "seconds")
            time.sleep(1)

        self.current_signal = "YELLOW"
        print("Signal:", self.current_signal)
        time.sleep(2)

        self.current_signal = "RED"
        print("Signal:", self.current_signal)
        time.sleep(2)


def simulate_signal():

    controller = SignalController()

    congestion_levels = ["Low","Medium","High"]

    while True:
        congestion = random.choice(congestion_levels)
        controller.run_signal_cycle(congestion)


simulate_signal()
```

---

## Component Interaction

```
Traffic Sensor → Traffic Data
        │
        ▼
Congestion Analyzer
        │
        ▼
Signal Controller
        │
        ▼
Traffic Signal Timing Update
```

---

## Summary

* System components communicate through REST APIs.
* Traffic data flows from sensors to analysis and signal control modules.
* Processed data is stored in the database and visualized via the dashboard.
