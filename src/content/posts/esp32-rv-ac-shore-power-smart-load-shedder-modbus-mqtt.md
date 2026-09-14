---
author: VanSpecs Technical Team
pubDatetime: 2026-09-12T23:44:42Z
title: "Designing an ESP32 RV AC Shore Power Smart Load Shedder: Integrating Modbus Energy Meters, Relay Interlocking, and MQTT Telemetry"
postSlug: "esp32-rv-ac-shore-power-smart-load-shedder-modbus-mqtt"
calculator: ac-load
category: Smart RV & IoT
featured: false
draft: false
tags:
  - Smart RV & IoT
  - Caravan
  - Off-Grid
  - ESP32
  - RV Smart Automation
  - MQTT Telemetry
  - Modbus RTU
  - AC Load Shedding
ogImage: "/images/esp32-rv-ac-shore-power-smart-load-shedder-modbus-mqtt.jpg"
description: "Comprehensive technical guide for Designing an ESP32 RV AC Shore Power Smart Load Shedder: Integrating Modbus Energy Meters, Relay Interlocking, and MQTT Telemetry."
---

The rising demand for off-grid living and enhanced RV campsite experiences often clashes with the limitations of low-amperage shore power connections. Campgrounds frequently impose strict limits, such as 6A, 10A, or 16A, making the simultaneous operation of high-draw AC appliances like electric water heaters, rooftop air conditioners, induction cooktops, and battery chargers a significant challenge, leading to frustrating breaker trips. This technical guide details the design and implementation of an ESP32-based intelligent AC load shedding system. This system proactively manages power consumption by dynamically shedding non-critical loads, ensuring continuous operation within shore power limits while maintaining essential functions.

## System Hardware Architecture

The core of this intelligent load shedding system revolves around the ESP32 microcontroller, chosen for its dual-core processing capabilities, integrated Wi-Fi, and robust peripheral set. The system interfaces with an AC energy meter, a multi-channel relay board, and incorporates essential safety components.

### Energy Meter Integration

For accurate real-time current and voltage monitoring, two primary energy meter options are considered:

1. **PZEM-004T V3.0:** This low-cost, readily available AC energy meter communicates via Hardware UART. It provides measurements for voltage, current, active power, frequency, and power factor. Its simplicity makes it suitable for many RV applications.
2. **SDM120 Modbus RTU:** A more industrial-grade option, the SDM120 communicates via Modbus RTU over RS485. This requires an RS485 to TTL converter module to interface with the ESP32's UART. The SDM120 offers higher accuracy and robustness, along with a richer set of parameters including apparent power and reactive power.

For this design, we will focus on the SDM120 Modbus RTU due to its superior features and industrial applicability, leveraging the ESP32's dedicated hardware UART for reliable communication. The RS485 interface provides excellent noise immunity over longer cable runs, which is beneficial in an RV environment.

### Optically Isolated Multi-Channel Relay Board

Switching high-current AC loads necessitates robust and safe relay modules. An optically isolated multi-channel relay board (e.g., 4-channel or 8-channel) is crucial. Optical isolation protects the low-voltage ESP32 circuitry from high-voltage AC transients and ground loops. Each relay controls a specific AC appliance.

### Snubber Circuits

Inductive AC loads, such as air conditioner compressors or water pump motors, generate significant back-EMF (electromotive force) when switched off. This can cause arcing across relay contacts, leading to premature failure and electrical noise. Snubber circuits, typically composed of a resistor and capacitor (RC snubber) in series, connected in parallel with the relay contacts, dissipate this energy, protecting the relays and improving system reliability. For larger inductive loads, metal oxide varistors (MOVs) can also be used in conjunction with or instead of RC snubbers for surge suppression.

### Zero-Cross Detection Modules

To minimize electrical noise and extend relay life, it is ideal to switch AC loads at the zero-crossing point of the AC waveform. A zero-cross detection module, typically an optocoupler-based circuit, provides a digital signal to the ESP32 indicating when the AC voltage crosses zero. The ESP32 can then time its relay switching commands to coincide with these zero-crossing points, reducing inrush current and arcing.

### Hardware Interlocking

Beyond software-based interlocking, critical load paths can benefit from hardware interlocking. For instance, if two high-power appliances cannot operate simultaneously from a safety perspective, physical wiring can prevent this. An example would be using a double-pole, double-throw (DPDT) relay to ensure only one of two loads is energized at any given time, regardless of the ESP32's state.



![Schematic showing ESP32, SDM120, RS485 converter, opto-isolated relays with snubbers, and zero-cross detection](/images/esp32-rv-ac-shore-power-smart-load-shedder-modbus-mqtt-part1.jpg)



## Load Shedding Prioritization Engine

The intelligence of the system lies in its ability to prioritize loads. This requires a clear classification and a dynamic shedding algorithm.

### Load Categorization and Prioritization

Loads are categorized based on their criticality and impact on the RV experience.

| Priority Level | Category | Example Appliances | Shedding Strategy |
| :--- | :--- | :--- | :--- |
| **P1 (Critical)** | Essential | LiFePO4 Charger, Refrigerator (AC mode), Starlink | Never shed unless extreme overload or safety dictates. |
| **P2 (High)** | Comfort/Necessity | Rooftop Air Conditioner, Electric Water Heater (AC) | Shed only when P1 loads consume significant power. |
| **P3 (Medium)** | Convenience | Induction Cooktop, Microwave, Space Heater | First to shed; re-engage when ample power available. |
| **P4 (Low)** | Non-Essential | Entertainment Systems (High-Power Audio), Toaster | Shed proactively to maintain P1/P2. |

### Prioritization Hierarchy Logic

The system operates based on a predefined hierarchy. When the total current draw approaches the shore power limit, loads are shed in reverse order of their priority (P4 first, then P3, and so on). When current drops below a re-engage threshold, loads are re-engaged in order of priority (P1 first, then P2, etc.).

### Dynamic Shed/Re-engage Thresholds

The system continuously monitors the RMS current drawn from the shore power using the SDM120. Thresholds are defined as percentages of the configured shore power limit.

* **Shed Threshold:** `Shore Power Limit * 0.90` (e.g., 90% of 16A = 14.4A)
* **Re-engage Threshold:** `Shore Power Limit * 0.70` (e.g., 70% of 16A = 11.2A)

This hysteresis band (14.4A for shedding, 11.2A for re-engaging) prevents rapid cycling of relays, which can reduce their lifespan and create an unstable user experience.

### Calculation Example: Shore Power Limit and Thresholds

**Inputs:**
* Shore Power Breaker Limit: 16 Amperes (A)
* Shedding Percentage: 90%
* Re-engagement Percentage: 70%

**Assumptions:**
* Stable AC voltage (e.g., 230V RMS).
* Purely resistive loads for simplicity, power factor close to 1.0. (In reality, the SDM120 measures true RMS current, so power factor doesn't directly affect the current limit itself, but rather the real power consumed).

**Formula:**
* Shed Threshold (A) = Shore Power Breaker Limit (A) * Shedding Percentage
* Re-engage Threshold (A) = Shore Power Breaker Limit (A) * Re-engagement Percentage

**Calculation:**
* Shed Threshold = 16 A * 0.90 = 14.4 A
* Re-engage Threshold = 16 A * 0.70 = 11.2 A

**Result:**
The system will initiate load shedding when the total measured current exceeds 14.4 A. Loads will be re-engaged when the total measured current drops below 11.2 A.

## Protection & Hysteresis Algorithms

Robust protection mechanisms are essential for system stability, safety, and longevity.

### Delay Timers

Rapid cycling of high-power loads, especially compressors (like in an AC unit), can cause damage. A minimum off-time delay (e.g., 3-5 minutes) should be implemented for such loads after they have been shed. This allows pressures to equalize and prevents immediate re-engagement, protecting the compressor from locked-rotor current issues. Similarly, a minimum on-time delay can prevent short cycling.

### Relay Interlocking Logic (Software & Hardware)

Beyond the hardware interlocking discussed earlier, software interlocking prevents contradictory relay states. For example, if two loads are mutually exclusive (e.g., two different heating elements in a multi-mode water heater), the software ensures only one can be active at a time. This logic is integrated into the load shedding engine.

### Hysteresis Bands

As calculated above, hysteresis (the difference between shedding and re-engagement thresholds) is critical. Without it, the system would rapidly switch loads on and off when the current fluctuates around a single threshold, leading to "chatter" and reduced relay life. The chosen 20% band (90% shed, 70% re-engage) provides a stable operating window.

## FreeRTOS Task Management on ESP32

Leveraging the ESP32's dual-core architecture with FreeRTOS is key to ensuring responsive and reliable operation.

### Core 0: High-Frequency Modbus Polling & Safety Interrupts

The primary core (Core 0) is dedicated to time-critical operations:

* **Modbus Polling:** A high-priority FreeRTOS task continuously polls the SDM120 energy meter via UART. This task should run at a frequency sufficient for real-time monitoring (e.g., every 100-250ms). It reads voltage, current, active power, and other relevant parameters.
* **Safety Interrupt Triggers:** External interrupt pins on the ESP32 can be configured for immediate safety actions. For instance, a hardware overcurrent trip signal (if available from an external current sensor) or a thermal sensor exceeding a critical threshold could trigger an immediate system-wide shutdown or shedding of all non-essential loads.
* **Load Shedding Engine:** The core logic for load prioritization and shedding decisions, based on the polled current data, also resides on Core 0 to ensure immediate response.

### Core 1: MQTT State Machine and Wi-Fi Stack

The secondary core (Core 1) handles network communication and less time-critical tasks:

* **Wi-Fi Stack:** Manages the Wi-Fi connection to the local network.
* **MQTT Client:** Publishes telemetry data (current, voltage, power, relay states, power factor, reactive power) to an MQTT broker. It also subscribes to command topics for remote control (e.g., manual override, changing shore power limits).
* **Home Assistant Auto-Discovery:** Publishes configuration topics to enable Home Assistant to automatically discover and integrate the device as various sensors, switches, and number entities.
* **Web Server (Optional):** A small web server for local configuration or diagnostic access.

This separation ensures that network latency or Wi-Fi stack operations do not interfere with the critical real-time monitoring and control functions on Core 0.

## MQTT & Home Assistant Integration

A robust MQTT integration provides remote monitoring, control, and seamless integration with smart home platforms like Home Assistant.

### MQTT JSON Payload Schema

Telemetry data is published as JSON payloads to structured topics.

**Example Topic: `rv/shore_power/telemetry`**

```json
{
  "timestamp": "2023-10-27T10:30:00Z",
  "total_current_rms_A": 12.5,
  "total_power_W": 2875.0,
  "voltage_V": 230.1,
  "frequency_Hz": 50.0,
  "power_factor": 0.98,
  "reactive_power_VAR": 400.0,
  "apparent_power_VA": 2933.0,
  "shore_limit_A": 16.0,
  "shed_threshold_A": 14.4,
  "reengage_threshold_A": 11.2,
  "load_shed_active": true,
  "loads": {
    "charger": {
      "state": "ON",
      "priority": 1,
      "current_A": 7.0
    },
    "ac_unit": {
      "state": "SHED",
      "priority": 2,
      "current_A": 6.5
    },
    "water_heater": {
      "state": "ON",
      "priority": 3,
      "current_A": 4.0
    },
    "cooktop": {
      "state": "OFF",
      "priority": 3,
      "current_A": 0.0
    }
  }
}
```

This comprehensive payload allows for detailed monitoring of the entire system state. Each load can also have its individual topic for control (e.g., `rv/loads/ac_unit/set` with payload `{"state": "ON"}` or `{"state": "OFF"}`).

### Home Assistant Auto-Discovery

The ESP32 can publish MQTT discovery messages to the `homeassistant/` topic, allowing Home Assistant to automatically create entities.

**Example for Total Current Sensor:**

```json
Topic: `homeassistant/sensor/rv_shore_power/total_current/config`
Payload:
{
  "name": "RV Shore Power Total Current",
  "state_topic": "rv/shore_power/telemetry",
  "value_template": "{{ value_json.total_current_rms_A }}",
  "unit_of_measurement": "A",
  "device_class": "current",
  "state_class": "measurement",
  "unique_id": "rv_shore_power_total_current",
  "device": {
    "identifiers": ["rv_shore_power_shedder_001"],
    "name": "RV Smart Shore Power",
    "model": "ESP32 Load Shedder",
    "manufacturer": "Custom"
  }
}
```

Similar configurations are published for voltage, power, frequency, power factor, and individual load switches. A `number` entity can be created for the `shore_limit_A` to allow users to dynamically adjust the shore power limit from the Home Assistant UI.

## Safety & Fail-Safe Mechanics

Safety is paramount when dealing with high-voltage AC systems. Multiple layers of fail-safes are integrated.

### Thermal Emergency Shutoff Logic

An NTC thermistor or digital temperature sensor (e.g., DS18B20) strategically placed near high-current components (e.g., main input terminals, relay board) monitors critical temperatures. If a predefined thermal threshold is exceeded, the ESP32 can trigger an immediate emergency shutdown, shedding all non-essential loads or even all loads if the temperature indicates a severe fault (e.g., wiring overheating). This is a critical safety measure.

### Relay Contact Weld Detection

Relay contacts can sometimes weld shut due to excessive current, arcing, or material fatigue. The system can implement a simple form of weld detection. After commanding a relay to "OFF," if the current measurement for that specific load (if individual load current sensing is implemented) or the total current does not drop as expected, it suggests the relay might be welded. In such a scenario, the system can alert the user, attempt to cycle the relay, and if unsuccessful, trigger a higher-level alarm or even a main breaker trip (if integrated with a smart circuit breaker).

### Default Fail-Safe Relay State Configuration

Relays have Normally Open (NO) and Normally Closed (NC) contacts. For fail-safe operation:

* **Critical Loads:** If a load absolutely *must* remain on in the event of controller failure (e.g., a critical medical device, or a small DC-powered refrigerator that also has an AC mode), it should be wired through a **Normally Closed (NC)** contact. This means if the ESP32 loses power or malfunctions, the relay de-energizes, and the NC contact closes, supplying power to the load. This is less common for high-power AC loads being *shed*, but important for overall system design.
* **Sheddable Loads:** For loads that are intended to be shed, wiring them through **Normally Open (NO)** contacts is standard. This ensures that if the ESP32 fails or loses power, these loads will default to the "OFF" state, preventing an uncontrolled overcurrent situation. Most load shedding systems will use NO contacts for the loads they control.

### Physical Manual Bypass Switch Wiring

Despite all digital controls, a physical manual bypass switch is an indispensable safety feature. This switch, typically a heavy-duty double-pole, double-throw (DPDT) switch, can completely bypass the entire smart load shedding system. In the "Bypass" position, shore power is routed directly to all RV AC circuits, completely isolating the ESP32 and relay board. This allows for troubleshooting, maintenance, or emergency operation without relying on the smart system. This switch should be easily accessible and clearly labeled.

## Sources and Assumptions

**Energy Meter Specifications:**
* SDM120 Modbus RTU: Datasheet specifies accuracy Class 1 for active energy, Class 2 for reactive energy. Communication protocol is Modbus RTU at 9600 bps (default). [Reference: Eastron SDM120 Series Energy Meter Datasheet]

**ESP32 Specifications:**
* ESP32-WROOM-32: Dual-core Tensilica Xtensa LX6 microprocessor, 240 MHz. Integrated Wi-Fi (802.11 b/g/n) and Bluetooth (v4.2 BR/EDR and BLE). Multiple UART interfaces. [Reference: Espressif ESP32 Datasheet]

**Relay Specifications:**
* Assumed relay contact rating: 30A @ 250VAC for high-power loads. This provides a significant safety margin for typical RV appliances. [Reference: Common industrial relay specifications, e.g., Omron G2R series]

**Shore Power Limits:**
* Common campsite limits: 6A, 10A, 16A, 30A (North America), 50A (North America). The system is configurable for these limits.

**Load Consumption (Assumed for example calculations):**
* LiFePO4 Charger: 1500W (approx. 6.5A @ 230V)
* Rooftop Air Conditioner: 1500W (approx. 6.5A @ 230V, excluding start-up surge)
* Electric Water Heater: 1000W (approx. 4.3A @ 230V)
* Induction Cooktop (single burner): 1800W (approx. 7.8A @ 230V)

**Hysteresis and Delay Timers:**
* Shedding Hysteresis: 20% of shore power limit (90% shed, 70% re-engage). This value is chosen as a balance between responsiveness and stability.
* Minimum AC Compressor Off-Time: 3 minutes. This is a standard recommendation to protect AC compressors.

**Communication Protocol:**
* MQTT v3.1.1 standard for telemetry and control.
* Home Assistant MQTT Discovery Protocol.

**Safety Standards:**
* All AC wiring should conform to local electrical codes (e.g., NEC in North America, BS 7671 in UK, VDE in Germany). Proper grounding, wire gauge selection, and overcurrent protection are critical and outside the scope of this control system's direct function, but assumed to be correctly implemented in the RV's main electrical system.
