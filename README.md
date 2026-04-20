## 3. Approach / Methodology

### 3.0 Introduction

This chapter outlines the methodology adopted for the design, implementation, and evaluation of the proposed **UNILIS Smart Laboratory System**. The methodology provides a clear, step-by-step approach to achieve the project objectives, which include automation of laboratory processes, integration of IoT and embedded systems, real-time monitoring, and enhanced academic support.

The chapter describes the overall research approach, system design principles, technologies employed, as well as the development, integration, testing, and evaluation processes.

### 3.1 Description of the Approach

The project adopts a **system implementation and development methodology** that combines **incremental prototyping** with **modular system integration**. 

The UNILIS Smart Laboratory System leverages **IoT devices**, **embedded systems**, **cloud computing**, and **AI-assisted analytics** to build a scalable, intelligent, and secure laboratory management platform. The methodology is designed to ensure the system meets both functional and non-functional requirements while remaining reliable, secure, and user-friendly for students, instructors, and laboratory staff.

### 3.1.1 Step-by-Step Approach

The development process follows a structured seven-step approach:

#### Step 1: Requirements Analysis
- Conduct a detailed study of current laboratory and academic processes in Kenyan universities, with focus on UNILIS usage.
- Identify key pain points in experiment automation, attendance tracking, laboratory safety monitoring, and data collection.
- Define functional requirements (e.g., sensor monitoring, data logging, dashboard access) and non-functional requirements (e.g., scalability, security, usability).
- Gather insights through interviews with laboratory staff, instructors, and students to refine system expectations.

#### Step 2: System Design
- Develop a **modular architecture** consisting of four primary layers:
  1. **Sensor & Actuator Layer** – IoT devices and sensors for environmental monitoring, actuators for equipment control.
  2. **Edge & Embedded Layer** – Microcontroller-based modules (ESP32, Arduino, STM32) for real-time data processing and control.
  3. **Cloud & Analytics Layer** – Data storage, processing, AI-based analytics, and seamless integration with UNILIS.
  4. **User Interface Layer** – Web and mobile dashboards for students and instructors, including notifications and reporting.
- Design system workflows, data flow diagrams, sensor-actuator mappings, and robust security protocols.

#### Step 3: Technology Selection and Setup
- Select appropriate IoT sensors and embedded boards suitable for scientific laboratories (temperature, humidity, gas, chemical, vibration sensors, etc.).
- Configure edge devices for sensor data acquisition, actuator control, and secure data transmission to the cloud.
- Set up cloud infrastructure including MySQL databases, Docker-hosted APIs, and AI analytics modules.
- Integrate the platform with the existing **UNILIS** system using secure APIs for authentication, role-based access control, and data synchronization.

#### Step 4: System Implementation
- Develop individual modules for sensor interfacing, data acquisition, actuation control, cloud storage, and dashboard visualization.
- Implement real-time monitoring and control using IoT protocols such as **MQTT**, **HTTP/HTTPS**, and **WebSocket**.
- Incorporate security mechanisms including data encryption, secure authentication, and role-based access control (RBAC).
- Integrate AI and analytics components to generate lab reports, predictive insights, and real-time alerts for anomalies or unsafe conditions.

#### Step 5: Integration and Testing
- Integrate all modules into a unified, cohesive platform.
- Perform **unit testing** on individual IoT and embedded modules.
- Conduct comprehensive **system testing** covering sensor-actuator responses, data logging accuracy, cloud analytics, and dashboard functionality.
- Carry out **User Acceptance Testing (UAT)** with students and instructors to validate usability and alignment with academic workflows.

#### Step 6: Evaluation and Refinement
- Evaluate the system against predefined project objectives, including automation efficiency, data accuracy, and improvement in student learning experience.
- Collect feedback from stakeholders and iteratively refine system performance, user interface, and security features.
- Document lessons learned, system limitations, and potential areas for future enhancement.

#### Step 7: Deployment and Maintenance
- Deploy the system in a controlled laboratory environment within a Kenyan university campus.
- Monitor system stability, scalability, and reliability during real-world operation.
- Establish a long-term maintenance plan for regular updates of software modules, sensor calibration, and embedded firmware.

---

This methodology ensures a systematic, iterative, and stakeholder-driven development process, resulting in a robust and practical smart laboratory solution tailored for higher education institutions in Kenya.