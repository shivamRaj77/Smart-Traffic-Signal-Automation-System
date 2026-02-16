# **I. Software Architecture Style**

## **Layered Architecture**

The Layered Architecture enables modular development, simplifies maintenance, and supports scalable traffic management across multiple junctions.  
---

## **I-A. Justification: Why this system fits Layered Architecture**

**Granularity of components:**

* The system is clearly divided into **logical layers**

* Each layer has a **single responsibility**

* Higher layers depend only on lower layers

**Layer Breakdown:**

* **Presentation Layer**

  * Traffic monitoring dashboard

  * Reports and analytics view for Traffic Administrator

* **Application / Logic Layer**

  * Traffic data processing

  * Congestion analysis

  * Signal timing optimization

* **Data Layer**

  * Traffic data storage

  * Signal logs

  * Historical analytics

This separation confirms the system follows a **Layered Architecture**.

Simple Layer Diagram:

\+----------------------------+  
|   Presentation Layer       |  
| (Reports, Analytics UI)    |  
\+----------------------------+  
|   Application Layer        |  
| (Congestion & Signal Logic)|  
\+----------------------------+  
|   Data Layer               |  
| (Traffic & Signal Data)    |  
\+----------------------------+

## **I-B. Why Layered Architecture is the Best Choice (5 Marks)**

### **Scalability**

* New junctions can be added without changing UI or database logic

* Analysis algorithms can be upgraded independently

### **Maintainability**

* Clear separation of concerns

* Changes in one layer do not affect others

### **Performance**

* Data processing is isolated from presentation

* Efficient traffic analysis without UI overhead

### **Flexibility**

* Supports future integration of:

  * Real sensors

  * Machine learning modules

  * Cloud databases

### **Academic Suitability**

* Simple to understand

* Easy to document using UML and DFDs

* Ideal for simulation-based systems

# **II. Application Components**

Below are the **core software components** of the system.

---

## **1\. Traffic Sensor Component**

* Collects vehicle count and speed

* Acts as the data input source

---

## **2\. Traffic Data Management Component**

* Stores raw and processed traffic data

* Manages timestamps and metrics

---

## **3\. Congestion Analysis Component**

* Calculates traffic density

* Classifies congestion levels (Low / Medium / High)

---

## **4\. Signal Control Component**

* Computes adaptive signal timings

* Updates traffic signal states

---

## **5\. Junction Management Component**

* Coordinates sensors and signal controllers

* Manages traffic flow per junction

---

## **6\. Traffic Monitoring Component**

* Oversees multiple junctions

* Generates system-level insights

---

## **7\. Reporting & Analytics Component**

* Generates traffic reports

* Provides visual analytics to administrators

---

## **8\. Data Storage Component**

* Stores traffic history

* Stores signal timing logs

---

## **9\. Configuration Component**

* Maintains system thresholds

* Manages signal timing limits

---

## **10\. Simulation Component**

* Generates synthetic traffic data

* Used for testing and evaluation

