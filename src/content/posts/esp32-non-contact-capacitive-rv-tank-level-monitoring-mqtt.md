---
author: VanSpecs Technical Team
pubDatetime: 2026-09-12T12:31:00Z
title: "Designing a Corrosion-Free ESP32 Non-Contact Capacitive RV Tank Level Monitoring System with MQTT Telemetry"
postSlug: "esp32-non-contact-capacitive-rv-tank-level-monitoring-mqtt"
calculator: water-sizing
category: Smart RV & IoT
featured: false
draft: false
tags:
  - Smart RV & IoT
  - Caravan
  - Off-Grid
  - ESP32
  - Smart RV
  - IoT
  - MQTT
  - Tank Sensor
ogImage: "/images/esp32-non-contact-capacitive-rv-tank-level-monitoring-mqtt.jpg"
description: "Comprehensive technical guide for Designing a Corrosion-Free ESP32 Non-Contact Capacitive RV Tank Level Monitoring System with MQTT Telemetry."
---

The pervasive issue of unreliable tank level monitoring in recreational vehicles (RVs) has long plagued owners, particularly concerning grey and black water tanks. Traditional immersion-type probe sensors are notoriously susceptible to fouling, corrosion, and calcification, leading to inaccurate readings and frequent maintenance. This technical guide outlines the design and implementation of a non-contact capacitive tank level monitoring system for RVs, leveraging ESP32 microcontrollers and MQTT telemetry to provide accurate, corrosion-free, and energy-efficient water level data. This system addresses the inherent flaws of conventional methods by employing external, non-invasive capacitive sensing, ensuring longevity and consistent performance.

## Hardware Architecture for Non-Contact Capacitive Sensing

The core of this system relies on non-contact capacitive sensing, which eliminates direct contact between the sensor and the tank's contents. This is achieved by adhering parallel strips of copper foil tape vertically to the exterior surface of the plastic water tanks. These strips form the plates of a capacitor, with the plastic tank wall and the water within acting as the dielectric medium. As the water level changes, the effective dielectric constant between the plates varies, resulting in a measurable change in capacitance.

To ensure robust and accurate readings, a guard trace design is critical for mitigating parasitic capacitance. A guard trace involves surrounding the active sensing electrode with a grounded or driven shield electrode. This guard trace shunts stray electric fields away from the sensing electrode, directing them to ground or a controlled potential, thereby minimizing interference from external noise sources and improving measurement stability. The copper foil tape for the sensing electrode should be approximately 1-inch wide, with a 0.25-inch gap separating it from a parallel 0.5-inch wide guard trace. Both strips should extend from the bottom to the top of the tank's sensing range.

For capacitance measurement, two primary integrated circuits are suitable: the ADS1115 I2C Analog-to-Digital Converter (ADC) or the MPR121 capacitive touch driver module. The ADS1115, a 16-bit ADC, offers high resolution and can be configured to measure the change in voltage across a known resistor in an RC circuit, where the unknown capacitance dictates the charge/discharge time. Alternatively, the MPR121 is specifically designed for capacitive sensing and can directly report capacitance values or touch events. Given its dedicated function, the MPR121 often simplifies the software implementation for capacitance measurement. For this design, the MPR121 is preferred due to its integrated capacitance-to-digital conversion capabilities, simplifying the ESP32's workload. The MPR121 communicates with the ESP32 via the I2C bus.



![Diagram illustrating external copper foil tape sensor with guard trace on an RV tank.](/images/esp32-non-contact-capacitive-rv-tank-level-monitoring-mqtt-part1.jpg)



## Electronic Circuit Diagram and Power Regulation

The ESP32 microcontroller, along with the MPR121 module, requires a stable and clean power supply. RV electrical systems typically operate on a 12V DC nominal voltage, which can be noisy and subject to fluctuations. Therefore, a robust power regulation circuit is essential.

The circuit design incorporates a low-dropout (LDO) linear regulator, such as the AMS1117-3.3, to convert the 12V RV supply to a stable 3.3V for the ESP32 and MPR121. To minimize noise and voltage ripple, a multi-stage filtering approach is employed. A large electrolytic capacitor (e.g., 470µF) should be placed at the input of the LDO to smooth out gross voltage fluctuations from the 12V supply. Following the LDO, smaller ceramic capacitors (e.g., 0.1µF and 10µF) should be placed as close as possible to the ESP32 and MPR121 power pins. These decoupling capacitors effectively shunt high-frequency noise to ground, ensuring a clean power rail.

A typical circuit diagram would involve:
*   **Input:** 12V DC from RV battery.
*   **Protection:** A fuse (e.g., 1A slow-blow) and a reverse polarity protection diode (e.g., 1N4001) at the 12V input.
*   **Voltage Regulation:** An AMS1117-3.3V LDO regulator.
*   **Input Capacitance for LDO:** 470µF electrolytic capacitor, followed by a 0.1µF ceramic capacitor.
*   **Output Capacitance for LDO:** 10µF electrolytic capacitor, followed by a 0.1µF ceramic capacitor.
*   **ESP32 Power:** VCC to 3.3V output of LDO, GND to LDO ground.
*   **MPR121 Power:** VDD to 3.3V output of LDO, GND to LDO ground.
*   **I2C Bus:** ESP32 SDA to MPR121 SDA, ESP32 SCL to MPR121 SCL. Pull-up resistors (e.g., 4.7kΩ) are recommended on SDA and SCL lines if not already present on the MPR121 module.

## Software and Filtering Algorithms

Raw capacitance readings from the MPR121 can be susceptible to environmental noise, temperature variations, and particularly in an RV, sloshing of water during movement or foaming. To provide stable and reliable tank level data, filtering algorithms are indispensable. This system employs either an Exponential Moving Average (EMA) or a Kalman Filter, implemented in C++ using the Arduino IDE or PlatformIO framework.

**Exponential Moving Average (EMA):**
EMA is a type of infinite impulse response filter that gives more weight to recent data points. It is computationally less intensive than a Kalman filter and often sufficient for smoothing out minor fluctuations.

Formula: `Filtered_Value = (Alpha * Current_Value) + ((1 - Alpha) * Previous_Filtered_Value)`
Where `Alpha` is the smoothing factor, a value between 0 and 1. A higher `Alpha` makes the filter more responsive to changes but less smooth; a lower `Alpha` makes it smoother but slower to react. For tank level monitoring, an `Alpha` of 0.1 to 0.2 is often a good starting point.

Example C++ implementation snippet:
```cpp
float alpha = 0.15; // Smoothing factor
float filteredCapacitance = 0.0; // Initial value

void setup() {
  // Initialize MPR121 and other sensors
  // ...
  filteredCapacitance = readRawCapacitance(); // Initialize with first reading
}

void loop() {
  float currentCapacitance = readRawCapacitance();
  filteredCapacitance = (alpha * currentCapacitance) + ((1 - alpha) * filteredCapacitance);
  // Use filteredCapacitance for further calculations
  // ...
  delay(100); // Small delay for sampling
}
```

**Kalman Filter:**
For more sophisticated noise reduction, especially in dynamic environments, a Kalman Filter provides an optimal estimation of the system's state. It is more complex to implement but offers superior performance by modeling the system's dynamics and measurement noise. It is particularly effective at handling transient events like sloshing without over-smoothing.

A basic Kalman filter implementation involves predicting the current state based on the previous state and then updating this prediction with the current measurement. This requires defining system parameters such as measurement noise covariance (R) and process noise covariance (Q).

Example C++ implementation (simplified conceptual outline):
```cpp
// Kalman Filter variables
float Q = 0.001; // Process noise covariance (adjust based on system dynamics)
float R = 0.01;  // Measurement noise covariance (adjust based on sensor noise)
float x_hat = 0.0; // Estimated state
float P = 1.0;   // Error covariance

void setup() {
  // Initialize MPR121 and other sensors
  // ...
  x_hat = readRawCapacitance(); // Initialize state with first reading
}

void loop() {
  float z = readRawCapacitance(); // Current measurement

  // Prediction step
  float x_hat_minus = x_hat;
  float P_minus = P + Q;

  // Update step
  float K = P_minus / (P_minus + R); // Kalman gain
  x_hat = x_hat_minus + K * (z - x_hat_minus);
  P = (1 - K) * P_minus;

  // Use x_hat (filtered capacitance) for further calculations
  // ...
  delay(100);
}
```
The choice between EMA and Kalman filter depends on the desired accuracy and computational resources. For most RV applications, a well-tuned EMA can provide sufficient stability.

## Calibration Calculation for Accurate Percentage Readings

Accurate tank level percentages require a calibration process to map raw capacitance values to physical tank levels. This involves reading the capacitance values for an empty tank (`C_empty`) and a full tank (`C_full`). These two points establish the linear range of the sensor.

**Calibration Steps:**
1.  **Empty Tank Reading:** Ensure the tank is completely empty. Record the filtered capacitance reading as `C_empty`.
2.  **Full Tank Reading:** Fill the tank completely. Record the filtered capacitance reading as `C_full`.
3.  **Linear Interpolation:** Once `C_empty` and `C_full` are known, any raw capacitance reading (`C_raw`) can be converted to a percentage using the following linear interpolation formula:

    `Percent = ((C_raw - C_empty) / (C_full - C_empty)) * 100`

    This formula assumes a linear relationship between capacitance and water level, which is a reasonable approximation for a uniform tank shape and sensor placement.

**Numerical Calculation Example:**
Assume the following calibrated values:
*   `C_empty` = 150 (arbitrary units from MPR121)
*   `C_full` = 850 (arbitrary units from MPR121)

Now, let's say a current reading `C_raw` is 400.
`Percent = ((400 - 150) / (850 - 150)) * 100`
`Percent = (250 / 700) * 100`
`Percent = 0.35714 * 100`
`Percent = 35.71%`

To convert the percentage to liters, the total capacity of the tank must be known.
Assumption: Tank Total Capacity = 100 Liters.
`Liters = (Percent / 100) * Tank_Total_Capacity`
`Liters = (35.71 / 100) * 100`
`Liters = 35.71 Liters`

This method provides a precise and reliable way to translate sensor data into actionable tank level information.

## MQTT Telemetry and Deep Sleep for Battery Optimization

Energy efficiency is paramount in RV applications, where power is typically supplied by batteries. The ESP32's deep sleep mode is critical for optimizing battery consumption. The system is designed to wake up periodically, take measurements, transmit data via MQTT, and then return to deep sleep.

**Operational Logic:**
1.  **Wake-up:** The ESP32 is configured to wake up from deep sleep every 5 minutes using its internal Real-Time Clock (RTC) timer.
2.  **Sensor Reading:** Upon waking, the ESP32 initializes the MPR121, reads the raw capacitance values for all monitored tanks, applies the chosen filtering algorithm (EMA or Kalman), and performs the calibration calculation to determine tank percentages and corresponding liter values.
3.  **Environmental Sensor (Optional but Recommended):** To enhance the utility of the system, a digital temperature sensor (e.g., DS18B20 or DHT11/22) can be included to monitor ambient temperature, which can affect sensor readings or provide useful environmental data.
4.  **Wi-Fi Connection:** The ESP32 connects to the RV's local Wi-Fi network. This connection should be as brief as possible to conserve power.
5.  **MQTT Publication:** Once connected, the ESP32 constructs a JSON data payload containing:
    *   `tank_id`: Identifier for the tank (e.g., "fresh_water", "grey_water_1").
    *   `percentage`: Calculated tank level percentage.
    *   `liters`: Calculated tank level in liters.
    *   `temperature`: Current sensor temperature (if integrated).
    *   `timestamp`: Time of measurement.

    This JSON payload is then published to a predefined MQTT topic (e.g., `rv/tanks/status`) on an MQTT broker. Home Assistant, a popular open-source home automation platform, can easily subscribe to these topics and display the data on its dashboard.
6.  **Deep Sleep:** After successfully publishing the MQTT message, the ESP32 disconnects from Wi-Fi and enters deep sleep mode until the next scheduled wake-up.

**Approximate Power Consumption:**
*   **Active Mode (Wi-Fi connected, sensors reading, MQTT publishing):** ~80-150mA for typically 5-10 seconds.
*   **Deep Sleep Mode:** ~10-20µA.

Over a 24-hour period, with a 5-minute wake-up interval:
*   Number of wake-ups: `24 hours * 60 minutes/hour / 5 minutes/wake-up = 288 wake-ups`
*   Total active time: `288 wake-ups * 10 seconds/wake-up = 2880 seconds = 48 minutes`
*   Total deep sleep time: `24 hours - 48 minutes = 23 hours 12 minutes`

**Assumptions:**
*   Average active current: 100mA
*   Average deep sleep current: 15µA

**Calculation of Daily Battery Consumption:**
*   Active consumption: `0.1A * (48/60) hours = 0.08 Ah`
*   Deep sleep consumption: `0.000015A * (23 + 12/60) hours = 0.000348 Ah`
*   Total daily consumption: `0.08 Ah + 0.000348 Ah = 0.080348 Ah`

This extremely low power consumption ensures that the system has a minimal impact on the RV's battery bank, allowing for extended off-grid operation.

## Comparison Matrix: Non-Contact Capacitive vs. Alternatives

To highlight the advantages of the proposed system, a comparison with common alternative tank level monitoring solutions is provided.

| Feature / Sensor Type           | Non-Contact Capacitive Sensors                                 | Ultrasonic Sensors                                          | Immersion-Type Probes (e.g., KIB, SeeLevel)                     |
| :------------------------------ | :------------------------------------------------------------- | :---------------------------------------------------------- | :-------------------------------------------------------------- |
| **Corrosion/Fouling Risk**      | **None** (external mounting)                                   | Low (transducer exposed to air/condensation, not water)     | **High** (direct contact with tank contents)                    |
| **Accuracy**                    | High (with proper calibration and filtering)                   | Moderate to High (affected by condensation, foam, temperature) | Low to Moderate (degrades significantly with fouling)           |
| **Installation**                | Moderate (external adhesion, wiring to ESP32)                  | Easy (top-mounted, requires drilling)                       | Moderate to Difficult (requires drilling, sealing, internal wiring) |
| **Maintenance**                 | **Very Low** (no moving parts, no contact)                     | Low (occasional cleaning of transducer face)                | **High** (frequent cleaning, probe replacement)                 |
| **Susceptibility to Foaming**   | Low (capacitance largely unaffected by surface foam)           | **High** (foam absorbs/ scatters ultrasonic waves)          | Low (probes are submerged)                                      |
| **Susceptibility to Sloshing**  | Moderate (requires software filtering)                         | Moderate (requires software filtering)                      | Low (probes are submerged)                                      |
| **Condensation Issues**         | None                                                           | **High** (condensation on transducer face distorts readings) | None                                                            |
| **Tank Material Compatibility** | Non-conductive tanks (plastic, fiberglass)                     | Most tank materials                                         | Most tank materials (probes are typically metal)                |
| **Cost**                        | Low to Moderate (copper tape, MPR121, ESP32)                   | Moderate (ultrasonic sensor module, ESP32)                  | Moderate to High (proprietary sensor arrays, display units)     |
| **Longevity**                   | **Excellent** (no contact, minimal wear)                       | Good (if protected from condensation)                       | **Poor** (due to corrosion and fouling)                         |

This comparison clearly demonstrates the superior long-term reliability and minimal maintenance requirements of non-contact capacitive sensing, especially when compared to the prevalent immersion-type probes.

## Second Comparison Table: Technical Parameters and Considerations

| Parameter                      | Non-Contact Capacitive System (ESP32/MPR121)                  | Ultrasonic Sensor System (ESP32/HC-SR04)                      |
| :----------------------------- | :------------------------------------------------------------ | :------------------------------------------------------------ |
| **Sensing Principle**          | Measures capacitance change due to dielectric constant shift | Measures time-of-flight of sound waves                       |
| **Sensor Placement**           | External, vertical strips on tank wall                        | Internal, top-mounted, downward-facing                        |
| **Required Tank Material**     | Non-conductive (Plastic, Fiberglass, Polypropylene)           | Any (as long as sound can propagate to liquid surface)        |
| **Min. Sensing Distance (Dead Zone)** | Negligible (sensor spans full height)                         | Typically 2-5 cm from transducer (cannot measure very top)    |
| **Max. Sensing Distance**      | Limited by sensor strip length (easily scalable)              | Up to 2-4 meters (depending on sensor model)                  |
| **Measurement Frequency**      | Configurable (e.g., every 5 minutes in deep sleep mode)       | Configurable (can be continuous or periodic)                  |
| **Environmental Impact**       | No direct contact with tank contents, inert materials         | No direct contact with tank contents, inert materials         |
| **Calibration Complexity**     | Two-point (empty/full) linear calibration                     | Single point (empty tank distance) or two-point               |
| **Power Consumption (Sensor Only)** | Very Low (MPR121 µA range)                                    | Low (HC-SR04 mA range during ping, µA idle)                   |
| **Interference Sources**       | Electrical noise, adjacent conductive surfaces                | Foam, condensation, irregular tank bottom, narrow beam angle  |
| **Data Output**                | Raw capacitance, filtered value, percentage, liters           | Distance to liquid, converted to percentage/liters            |

This detailed comparison reinforces the design choice, particularly highlighting the non-contact capacitive system's robustness against common issues like foam and condensation, which severely impact ultrasonic sensors.

## Sources and Assumptions

**Sources:**
*   **ESP32 Datasheet:** Espressif Systems. (n.d.). *ESP32 Series Datasheet*. Retrieved from [https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf)
*   **MPR121 Datasheet:** Freescale Semiconductor. (n.d.). *MPR121: Proximity Capacitive Touch Sensor Controller Datasheet*. Retrieved from [https://cdn-shop.adafruit.com/datasheets/MPR121.pdf](https://cdn-shop.adafruit.com/datasheets/MPR121.pdf)
*   **AMS1117-3.3 Datasheet:** Advanced Monolithic Systems. (n.d.). *AMS1117 1A Low Dropout Voltage Regulator Datasheet*. Retrieved from [https://www.advanced-monolithic.com/pdf/ds1117.pdf](https://www.advanced-monolithic.com/pdf/ds1117.pdf)
*   **Kalman Filter Principles:** Welch, G., & Bishop, G. (2006). *An Introduction to the Kalman Filter*. University of North Carolina at Chapel Hill.

**Assumptions:**
*   **Tank Material:** All RV tanks are assumed to be made of non-conductive plastic (e.g., polyethylene, polypropylene, ABS) with a relatively uniform wall thickness, which is a common standard in RV manufacturing.
*   **Water Properties:** The dielectric constant of grey and black water is assumed to be similar enough to fresh water for consistent capacitive sensing, although minor variations may exist due to dissolved solids.
*   **Linearity of Capacitance:** The relationship between water level and capacitance is assumed to be approximately linear over the tank's height for practical purposes, especially with careful sensor strip placement.
*   **Wi-Fi Availability:** A stable Wi-Fi network is assumed to be available within the RV for MQTT communication.
*   **MQTT Broker:** An MQTT broker (either local or cloud-based) is assumed to be accessible by the ESP32.
*   **Battery Voltage:** The RV's 12V supply is assumed to be within the operating range of the LDO regulator (typically 4.5V to 15V for AMS1117-3.3).
*   **Component Specifications:** Manufacturer specifications for current draw (ESP32, MPR121) and LDO efficiency are based on typical values and datasheets. Actual consumption may vary slightly depending on specific models and operating conditions.
