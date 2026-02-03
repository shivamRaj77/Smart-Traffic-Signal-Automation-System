# Software Requirements Specification (SRS)

## Project: Smart Traffic Signal Automation System

**Course:** CS331 Software Engineering Lab

**Members:**

          Shivam Panwar - 2301200
          Shivam Raj - 2301202
          Uddhav Singh Tomar - 2301235

---

## 1. Introduction

### 1.1 Purpose

This document specifies the functional and non-functional requirements of the Smart Traffic Signal Automation System. It serves as a reference for developers, evaluators, and stakeholders to understand system behavior and constraints.

### 1.2 Scope

The system automates traffic signal control at road junctions by analyzing traffic congestion and dynamically adjusting signal timings. The project focuses on software-level automation and simulation; physical traffic signal hardware control is outside the scope.

### 1.3 Definitions, Acronyms, and Abbreviations

| Term       | Description                                      |
| ---------- | ------------------------------------------------ |
| SRS        | Software Requirements Specification              |
| Junction   | A four-way traffic intersection                  |
| Congestion | Traffic density based on vehicle count and speed |
| NFR        | Non-Functional Requirement                       |
| FR         | Functional Requirement                           |

### 1.4 References

* IEEE 830 / IEEE 29148 Software Requirements Specification Standards
* Research literature on smart traffic management systems

---

## 2. Overall Description

### 2.1 Product Perspective

The Smart Traffic Signal Automation System functions as an intelligent decision-support layer within a smart city environment. It analyzes traffic conditions and determines optimal signal timings to reduce congestion.

### 2.2 Product Functions

* Collect traffic data per junction
* Detect congestion per direction
* Dynamically adjust traffic signal timings
* Monitor and analyze multiple junctions
* Identify critical congestion points

### 2.3 User Classes and Characteristics

| User                 | Description                                      |
| -------------------- | ------------------------------------------------ |
| Traffic Operator     | Monitors traffic conditions and system output    |
| System Administrator | Maintains and configures the system              |
| Student/Researcher   | Uses the system for analysis and experimentation |

### 2.4 Operating Environment

* Python-based software system
* Desktop or laptop computer
* Simulated traffic input data

### 2.5 Design and Implementation Constraints

* Simulation-based traffic data
* No physical signal hardware integration
* Academic time and resource limitations

### 2.6 Assumptions and Dependencies

* Traffic flows follow basic lane discipline
* Input data is reasonably accurate
* Time synchronization exists between system components

---

## 3. Functional Requirements (FR)

### 3.1 Traffic Data Acquisition & Monitoring

* **FR-1.01:** The system shall collect traffic data including vehicle count and average speed for each direction of a junction.
* **FR-1.02:** The system shall support synthetic traffic data generation for testing and simulation.
* **FR-1.03:** The system shall periodically update traffic data to reflect current conditions.

### 3.2 Congestion Detection & Analysis

* **FR-2.01:** The system shall compute congestion levels using traffic parameters.
* **FR-2.02:** The system shall classify congestion into Low, Medium, and High levels.
* **FR-2.03:** The system shall maintain congestion data independently for each junction.

### 3.3 Adaptive Signal Timing Control

* **FR-3.01:** The system shall dynamically calculate green signal duration based on congestion.
* **FR-3.02:** The system shall enforce a minimum green time for all directions.
* **FR-3.03:** The system shall allocate longer green times to more congested directions.

### 3.4 Multi-Junction Traffic Coordination

* **FR-4.01:** The system shall support multiple interconnected junctions.
* **FR-4.02:** The system shall analyze congestion independently for each junction.
* **FR-4.03:** The system shall identify the most congested junction.

### 3.5 Decision Support & Monitoring Interface

* **FR-5.01:** The system shall display congestion levels and signal timings.
* **FR-5.02:** The system shall highlight critical junctions requiring attention.
* **FR-5.03:** The system shall provide human-readable traffic management suggestions.

---

## 4. Non-Functional Requirements (NFR)

* **NFR-01 (Performance):** The system shall compute signal timings within a time suitable for real-time operation.
* **NFR-02 (Scalability):** The system shall support expansion to additional junctions.
* **NFR-03 (Reliability):** The system shall operate correctly under varying traffic conditions.
* **NFR-04 (Usability):** The system shall present outputs clearly for traffic operators.
* **NFR-05 (Maintainability):** The system shall be modular and easy to update.
* **NFR-06 (Extensibility):** The system shall allow future integration with real sensors and smart city infrastructure.

---

## 5. External Interface Requirements

### 5.1 User Interfaces

* Traffic monitoring dashboard
* Visualization of signal timings

### 5.2 Hardware Interfaces

* Simulated traffic sensors
* Future camera or IoT sensor integration

### 5.3 Software Interfaces

* Python libraries for data processing
* Visualization and plotting libraries

---

## 6. Data Requirements

* Vehicle count per direction
* Average vehicle speed
* Congestion levels
* Signal timing durations

---

## 7. Security Requirements

* Restricted access for system configuration
* Secure storage of configuration files

---

## 8. Quality Attributes

* High availability
* Fault tolerance
* Efficient resource usage

---

## 9. Future Enhancements

* Integration with real-time traffic sensors
* Emergency vehicle priority handling
* Predictive traffic analysis using machine learning

---

## 10. Appendices

* Sample traffic data formats
* Congestion calculation formulas
* System architecture diagrams
