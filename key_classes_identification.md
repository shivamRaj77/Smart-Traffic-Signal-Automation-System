# Identification of Key Classes

## Project: Smart Traffic Signal Automation System

**Course:** CS331 Software Engineering Lab

**Group:** 19

---

## 1. TrafficSensor

**Description:**
Represents a physical or simulated traffic sensor responsible for collecting raw traffic data from a specific direction of a junction.

**Attributes:**

* `- sensorId : String`
* `- location : String`
* `- direction : String`

**Methods:**

* `+ getVehicleCount() : int`
* `+ getAverageSpeed() : float`

---

## 2. TrafficData

**Description:**
Encapsulates traffic-related parameters collected from traffic sensors for further processing and analysis.

**Attributes:**

* `- vehicleCount : int`
* `- averageSpeed : float`
* `- timestamp : DateTime`

**Methods:**

* `+ calculateDensity() : float`
* `+ getTrafficMetrics() : Map`

---

## 3. CongestionAnalyzer

**Description:**
Analyzes traffic data to determine the congestion level at a junction.

**Attributes:**

* `# lowThreshold : float`
* `# highThreshold : float`

**Methods:**

* `+ analyzeCongestion(data : TrafficData) : String`

---

## 4. SignalController

**Description:**
Controls and manages traffic signal timings based on congestion analysis.

**Attributes:**

* `- minGreenTime : int`
* `- maxGreenTime : int`
* `- currentMode : String`

**Methods:**

* `+ computeSignalTiming(congestionLevel : String) : int`
* `+ updateSignalTiming(time : int) : void`

---

## 5. Junction

**Description:**
Represents a traffic junction consisting of multiple sensors and a signal controller.

**Attributes:**

* `- junctionId : String`
* `- sensors : List<TrafficSensor>`
* `- signalController : SignalController`

**Methods:**

* `+ collectTrafficData() : TrafficData`
* `+ manageSignals() : void`

---

## 6. TrafficMonitor

**Description:**
Provides system-level monitoring, analytics, and reporting functionality for traffic conditions.

**Attributes:**

* `- junctionList : List<Junction>`

**Methods:**

* `+ generateReport() : void`
* `+ viewAnalytics() : void`

---

## Visibility Legend

* `+` Public
* `-` Private
* `#` Protected
