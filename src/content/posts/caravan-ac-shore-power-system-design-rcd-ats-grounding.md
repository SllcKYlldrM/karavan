---
author: VanSpecs Technical Team
pubDatetime: 2026-09-15T07:27:59Z
title: "Complete RV AC Shore Power System Engineering: Dynamic Neutral-Ground Bonding, Dual RCD/GFCI Topologies, and Interlocked ATS Integration"
postSlug: "caravan-ac-shore-power-system-design-rcd-ats-grounding"
scope: caravan
category: Electrical & Wiring
subcategory: AC Shore Power
contentType: complete-system-case-study
topicCluster: "caravan / Electrical & Wiring / AC Shore Power"

relatedGuides:
  - "caravan-12v-cable-size-voltage-drop-calculator"
  - "off-grid-caravan-dc-dc-charger-efficiency-wiring-grounding"
featured: false
draft: false
tags:
  - AC Shore Power
  - Neutral Ground Bonding
  - RCD Selection
  - Transfer Switch Safety
  - Caravan Wiring
ogImage: "/images/caravan-ac-shore-power-system-design-rcd-ats-grounding.jpg"
description: "Master off-grid caravan AC mains safety: learn dynamic neutral-ground bonding relays, Type-A/B RCD selection, and mechanically interlocked ATS installation."
lastReviewed: 2026-09-15T07:27:59Z
---

The design and implementation of an AC shore power system in recreational vehicles (RVs) and tiny homes demands meticulous engineering to ensure safety, reliability, and compliance with electrical codes. This guide details advanced concepts for robust RV AC electrical infrastructure, focusing on dynamic neutral-ground bonding, comprehensive RCD/GFCI topologies, interlocked automatic transfer switch (ATS) integration, and intelligent load shedding strategies. These elements are critical for safeguarding occupants and equipment from electrical hazards, particularly when transitioning between shore power and inverter operation.

## Dynamic Neutral-Ground (N-G) Bonding Switch Logic

A fundamental safety principle in AC electrical systems is proper neutral-ground bonding. In an RV, the source of AC power can vary: it might be supplied by an external shore power connection (utility grid) or an onboard inverter. The key challenge is to ensure that the neutral and ground conductors are bonded *only* at the primary source of power. Incorrect bonding can lead to dangerous ground loops, nuisance tripping of protective devices, or even electrocution hazards.

### Shore Power Mode

When connected to shore power, the RV's electrical system becomes an extension of the utility grid. In this scenario, the neutral-ground bond is established at the utility's service entrance (or the shore power pedestal's distribution panel). Therefore, the RV's internal AC system *must not* have its own neutral-ground bond. The neutral conductor should be isolated from the chassis ground within the RV to prevent multiple bonding points, which can cause current to flow on the ground wire during normal operation.

### Inverter Mode

When operating solely from an onboard inverter, the inverter becomes the primary source of AC power. For safety, the inverter's output neutral must be bonded to the RV's chassis ground. This creates a "separately derived system," mimicking the safety characteristics of a utility service. If this bond is absent, a single fault to ground would not trip overcurrent protection, leaving metallic enclosures potentially live.

### Dynamic Bonding Implementation

To manage this critical distinction, a dynamic neutral-ground bonding switch, often controlled by a relay, is essential. This relay actuates based on the detected power source.

**Ground Relay Operation Flowchart:**

1.  **System Initialization:**
    *   Default state: Neutral-Ground bond *open*.
2.  **Shore Power Detection:**
    *   If shore power is detected as active and stable (e.g., via voltage sensing at the ATS input):
        *   Ensure the neutral-ground bonding relay remains *open*.
        *   The ATS switches to shore power input.
        *   The inverter's AC output is disconnected from the main AC panel.
3.  **Inverter Power Detection:**
    *   If shore power is *not* detected or is interrupted, and the inverter is active and supplying AC power:
        *   Activate the neutral-ground bonding relay to *close* the bond between the inverter's output neutral and the RV's chassis ground.
        *   The ATS switches to inverter output.
        *   This ensures proper grounding for the separately derived inverter system.
4.  **Transition Logic:**
    *   When transitioning from inverter to shore power, the neutral-ground bonding relay *must open* *before* the ATS connects the shore power input.
    *   When transitioning from shore power to inverter, the neutral-ground bonding relay *must close* *after* the ATS connects the inverter output.
    *   Many modern inverters and ATS units have integrated N-G switching logic, simplifying this, but external relays may be needed for older systems or specific configurations.



![Diagram illustrating dynamic neutral-ground bonding relay logic with shore power and inverter inputs](/images/caravan-ac-shore-power-system-design-rcd-ats-grounding-part1.jpg)



This dynamic switching prevents hazardous conditions such as floating neutrals or ground loops, which are common causes of electrical shocks or equipment damage in RVs.

## RCD/GFCI & MCB Protection Topologies

Residual Current Devices (RCDs) in Europe (or Ground Fault Circuit Interrupters (GFCIs) in North America) and Miniature Circuit Breakers (MCBs) are paramount for electrical safety. Their correct selection and placement are crucial for protecting against electrocution and overcurrents.

### RCD/GFCI Selection: Type A vs. Type B

RCDs are designed to detect leakage currents to earth. However, not all leakage currents are the same. Modern inverters, especially those with active power factor correction (PFC) or variable frequency drives (VFDs) for motor loads (like air conditioners), can produce complex leakage current waveforms.

*   **Type A RCD/GFCI:** Designed to detect sinusoidal AC residual currents and pulsating DC residual currents. These are common and suitable for many standard loads.
*   **Type B RCD/GFCI:** Essential for circuits supplied by inverters, EV charging points, or equipment with three-phase rectifiers. Type B RCDs can detect sinusoidal AC, pulsating DC, *and* smooth DC residual currents. Inverters often generate smooth DC leakage components due to their internal DC links and switching components. Using a Type A RCD with such loads can lead to a dangerous situation where a DC fault current goes undetected, potentially disabling the RCD.

**Recommendation:** For an RV system incorporating an inverter, it is highly recommended to use **Type B RCDs** for the main incoming AC supply from both shore power and inverter output, or at least for circuits known to be supplied by the inverter and potentially driving complex loads.

### Dual-Pole (DP) MCBs and RCDs

For safety, all AC circuits in an RV should ideally be protected by dual-pole (DP) circuit breakers and RCDs. This means both the phase (live) and neutral conductors are disconnected simultaneously in the event of an overcurrent or fault. This is critical in systems where polarity might be reversed (e.g., some international shore power connections) or to ensure complete isolation during maintenance.

**Typical Protection Topology:**

1.  **Main Shore Power Inlet:** A main DP MCB (e.g., 16A/30A) followed by a Type B RCD (e.g., 30mA trip current) protects the entire RV from the shore power connection.
2.  **Inverter Output:** The inverter's AC output should also pass through a Type B RCD (e.g., 30mA) and a DP MCB before feeding the main AC distribution panel. Some inverters have integrated RCD functionality; verify its type and sensitivity.
3.  **Branch Circuits:** Each individual AC appliance circuit (e.g., air conditioner, water heater, outlets) should be protected by its own appropriately sized DP MCB. For circuits supplying general-purpose outlets, additional individual RCD/GFCI protection (e.g., 10mA or 30mA) at the outlet level or as a sub-distribution RCD may be required by local codes.

**Example RCD/GFCI & MCB Configuration Table:**

| Component | Location | Type | Rating (Current/Sensitivity) | Poles | Function |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Main Shore Power Breaker | Shore Power Inlet | MCB | 16A / 30A | DP | Overcurrent protection from shore |
| Main Shore Power RCD | After Main Shore Power Breaker | RCD Type B | 30mA | DP | Earth fault protection from shore |
| Inverter Output Breaker | Inverter AC Output | MCB | Inverter Max Output (e.g., 20A) | DP | Overcurrent protection from inverter |
| Inverter Output RCD | After Inverter Output Breaker | RCD Type B | 30mA | DP | Earth fault protection from inverter |
| Air Conditioner | Dedicated Circuit | MCB | 10A / 15A (Load Dependent) | DP | Overcurrent protection for AC |
| Water Heater | Dedicated Circuit | MCB | 6A / 10A (Load Dependent) | DP | Overcurrent protection for water heater |
| General Outlets | Sub-Distribution or Individual Outlets | MCB + RCD | 10A / 30mA | DP | Overcurrent & earth fault for general loads |

## Mechanically Interlocked Automatic Transfer Switch (ATS) Architecture

An ATS is crucial for seamlessly switching between shore power and inverter power. The primary safety requirement for an ATS is to prevent "backfeeding," where the inverter could feed power back into the shore power inlet (or vice-versa), creating a severe electrocution hazard for utility workers or anyone handling the shore power cable. Mechanical interlocking is the most reliable method to prevent this.

### Interlocking Mechanism

A mechanically interlocked ATS ensures that only one power source can be connected to the RV's main AC distribution panel at any given time. This is achieved through a physical mechanism that prevents both contactors (or switches) from being closed simultaneously.

**ATS Operation:**

1.  **Shore Power Priority:** Typically, shore power is given priority. When shore power is detected and stable, the ATS connects the shore power input to the RV's AC panel.
2.  **Inverter Takeover:** If shore power is lost or unstable, the ATS waits for a pre-set delay (to prevent rapid cycling) and then switches to the inverter output, provided the inverter is active and producing power.
3.  **Return to Shore Power:** When shore power returns and stabilizes, the ATS again waits for a delay and then switches back to shore power.

**Wiring Diagram Concept:**

*   **Input 1:** Shore Power (Phase, Neutral, Earth)
*   **Input 2:** Inverter AC Output (Phase, Neutral, Earth)
*   **Output:** RV Main AC Distribution Panel (Phase, Neutral, Earth)

The ATS internally manages the switching of all three conductors (Phase, Neutral, Earth) for both inputs to the single output. Crucially, the neutral and earth conductors must also be switched correctly, especially in conjunction with the dynamic N-G bonding discussed earlier. Some ATS units integrate the N-G bonding relay, simplifying wiring.



![Simplified wiring diagram of a mechanically interlocked ATS with shore power, inverter, and RV load connections](/images/caravan-ac-shore-power-system-design-rcd-ats-grounding-part2.jpg)



**Safety Note:** Always use an ATS rated for the maximum expected current and voltage. Ensure proper grounding of the ATS enclosure. Consult the manufacturer's specific wiring diagrams.

## Manual and Automatic Load Shedding Infrastructure

RV electrical systems often operate with limited power budgets, especially when connected to lower-amperage shore power pedestals (e.g., 10A or 16A in Europe, 15A or 20A in North America) or when running demanding appliances from an inverter. Load shedding is the process of intelligently deactivating non-essential loads to prevent overloads and tripped breakers.

### Shore Power Current Limit Management

Many modern RVs and inverters feature a programmable shore power current limit. When this limit is set, the inverter (if it has pass-through and power assist features) will monitor the incoming shore power current. If the total RV load exceeds this limit, the inverter can either:
1.  **Supplement with Battery Power (Power Assist):** Briefly draw power from the battery to cover peaks, preventing the shore breaker from tripping.
2.  **Signal Load Shedding:** Trigger external relays to shed non-essential loads.

### Load Prioritization

Loads should be categorized by priority:

*   **Essential Loads:** Lights, water pump, refrigerator (if AC-powered), critical electronics. These should ideally remain powered.
*   **High-Priority Non-Essential:** Air conditioner, microwave, water heater. These are typically the first to be shed.
*   **Low-Priority Non-Essential:** Entertainment systems, auxiliary heaters.

### Implementation Strategies

1.  **Manual Load Shedding:** The simplest form. The user manually switches off high-power appliances when an overload is anticipated or occurs. This relies on user awareness and can be inconvenient.
2.  **Automatic Load Shedding (Relay-Based):**
    *   **Current Sensor:** A current transformer (CT) or shunt monitors the total AC current drawn from shore power or the inverter.
    *   **Control Module:** A dedicated load shedding controller (or a programmable relay within the inverter/charger) receives the current data.
    *   **Relays/Contactors:** When the current approaches the set limit, the controller activates relays to disconnect pre-selected high-power circuits (e.g., air conditioner compressor, water heater element).
    *   **Staged Shedding:** For more sophisticated systems, loads can be shed in stages. For example, if current exceeds 80% of the limit, the water heater is shed. If it exceeds 95%, the air conditioner is shed.
    *   **Reconnection Logic:** Once the current drops below a safe threshold for a defined period, the loads can be reconnected, typically in reverse order of shedding, with delays to prevent sudden inrush currents.

**Example Load Shedding Sequence (16A Shore Power Limit):**

| Current Threshold | Action | Affected Load |
| :--- | :--- | :--- |
| > 14A (87.5%) | Shed Stage 1: Disconnect | Electric Water Heater |
| > 15.5A (96.8%) | Shed Stage 2: Disconnect | Air Conditioner |
| < 12A (75%) | Reconnect Stage 1: Re-enable | Electric Water Heater |
| < 10A (62.5%) | Reconnect Stage 2: Re-enable | Air Conditioner |

**Numerical Example: Air Conditioner Load Calculation**

Let's assume an RV is connected to a 16A shore power supply (230V AC). The air conditioner draws 7A, and the electric water heater draws 5A. Other essential loads (fridge, lights, electronics) draw 3A.

*   **Total Load (AC + Water Heater + Essentials):** 7A + 5A + 3A = 15A
*   **Shore Power Limit:** 16A
*   **Remaining Capacity:** 16A - 15A = 1A

If the microwave (e.g., 6A) is turned on, the total load would be 15A + 6A = 21A, exceeding the 16A limit.

**Load Shedding Logic:**
1.  If a current sensor detects total draw approaching 15A (e.g., 90% of 16A = 14.4A), the load shedding system could first disable the water heater.
2.  **New Total Load:** 7A (AC) + 3A (Essentials) = 10A. This is now well within the 16A limit, allowing the microwave to operate.
3.  If the AC is then turned off, and the current drops below a threshold (e.g., 8A), the water heater could be re-enabled.

This intelligent management significantly enhances the usability and safety of the RV's electrical system, preventing frequent breaker trips and ensuring critical functions remain operational. For further details on DC system optimization, explore our guide on [Optimizing Off-Grid Caravan DC-DC Charger Efficiency: Advanced Wiring & Grounding Techniques](/posts/off-grid-caravan-dc-dc-charger-efficiency-wiring-grounding). To understand broader electrical system considerations, you can [Explore Caravan Systems](/scopes/caravan-systems/).

## Safety and Responsibility Disclaimer

Working with AC high voltage (120V/230V) carries a significant risk of severe injury or death. All electrical installations and modifications discussed in this guide must be performed by qualified and licensed professionals in strict accordance with local electrical codes and standards (e.g., IEC 60364-7-721 for caravans and motorhomes, or NEC Article 551 for Recreational Vehicles). The current and voltage ratings provided are typical design assumptions and illustrative; specific inverter, ATS, and appliance manufacturer guidelines are binding and must be followed. This document is for informational purposes only and does not constitute professional electrical engineering advice.

## Sources and Assumptions

*   **IEC 60364-7-721:** Requirements for special installations or locations – Caravans and motor caravans. (Illustrative standard for general guidance)
*   **National Electrical Code (NEC) Article 551:** Recreational Vehicles and Recreational Vehicle Parks. (Illustrative standard for general guidance)
*   **RCD/GFCI Types:** Information based on general electrical safety standards for residual current devices.
*   **Current/Voltage Ratings:** All current and voltage values (e.g., 10A, 16A, 230V, 30mA) are illustrative for typical RV installations and should be verified against actual component specifications and local regulations.
*   **Manufacturer Specifications:** Specific operational parameters for inverters, ATS units, and RCDs/GFCIs are assumed to be adhered to as per their respective manufacturer's instructions.
*   **Load Calculations:** Appliance current draws (e.g., 7A for AC, 5A for water heater) are illustrative averages and will vary by specific appliance model.
