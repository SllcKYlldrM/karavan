---
author: VanSpecs Technical Team
pubDatetime: 2026-09-11T20:30:45Z
title: "Diesel Heater High-Altitude Calibration: Adjusting ECU Pulse Frequency & Air-Fuel Mixture to Prevent Soot Clogging"
postSlug: "diesel-heater-high-altitude-ecu-pulse-frequency-air-fuel-mixture"
category: HVAC & Climate Control
calculator: heater-runtime
scope: caravan
subcategory: Heating & Ventilation
featured: false
draft: false
tags:
  - HVAC & Climate Control
  - Diesel Heater
  - High-Altitude Maintenance
  - Air-Fuel Ratio
  - Caravan HVAC
description: "A safety-focused guide to high-altitude diesel-heater operation, manufacturer-approved compensation and soot prevention."
---

## Safety boundary

Diesel heaters produce carbon monoxide and hot exhaust. Install and operate the heater exactly as specified by its manufacturer, route exhaust outside the living space, provide combustion air, keep a working carbon-monoxide alarm inside the vehicle and stop immediately if the alarm activates. Do not tune fuel delivery by guesswork. A high-altitude setting, kit or ECU adjustment is safe only when supported by the exact heater manual and verified by a qualified technician.

## Why altitude changes combustion

Atmospheric pressure and oxygen density decrease with altitude. If a heater continues to deliver the same fuel while less oxygen reaches the combustion chamber, combustion can become incomplete. Common symptoms include persistent smoke, soot at the exhaust, difficult starts, flame-outs, reduced heat output and increased carbon-monoxide risk. These symptoms can also be caused by blocked intake or exhaust pipes, a dirty burner screen, poor fuel quality, a weak glow plug or an incorrectly installed fuel line.

The fuel pump is usually controlled by timed pulses. Some controllers display frequency in hertz, while others display pulses per minute. The basic conversion is:

`Pulses per minute = frequency in hertz × 60`

This describes the control signal only. It does not prove that fuel volume is linear with frequency, because pump stroke, hose geometry, temperature and wear also affect delivery.

## Manufacturer-first adjustment workflow

1. Identify the exact heater model, controller, firmware and fuel-pump specification.
2. Read the manual for its approved altitude range and high-altitude mode.
3. Inspect intake, exhaust, fuel line, filter, burner screen and electrical supply before changing settings.
4. Confirm that a carbon-monoxide alarm is working and that ventilation is adequate.
5. Use the manufacturer’s high-altitude kit or automatic compensation when available.
6. Record the original settings before any permitted adjustment.
7. Make only the small adjustment described by the manual, then test at the permitted power levels.

## Planning estimate, not a calibration value

Atmospheric density can be estimated with a standard-atmosphere model, but a density ratio is not a universal fuel-reduction instruction. Heater fan curves, combustion-chamber geometry and control algorithms differ. For example, if a manufacturer-approved test procedure defines a 300 pulses-per-minute sea-level reference and provides a 0.69 altitude factor for a specific operating point, the arithmetic is:

`Reference pulse rate × approved factor = 300 × 0.69 = 207 pulses per minute`

This is only a worked calculation. Do not apply 207 PPM to another heater, controller or altitude without the manufacturer’s data and a safe verification procedure.

## Verification checklist

After any approved adjustment, monitor the heater during start-up, steady operation and shutdown. Record ambient temperature, altitude, controller setting, voltage, visible exhaust and carbon-monoxide readings. A clean-looking exhaust is not proof of safe combustion, and a low display reading on an inexpensive detector is not certification. Stop and investigate if the heater produces persistent white or black smoke, repeated flame-outs, unusual noise, fuel odor, overheating, or any CO alarm.

| Condition | Action |
| --- | --- |
| Persistent smoke or soot | Shut down safely and inspect; do not keep lowering fuel blindly |
| CO alarm or unexplained CO reading | Leave the area, ventilate and obtain professional inspection |
| Flame-out after adjustment | Restore the approved setting and follow the manual |
| Restricted intake or exhaust | Stop using the heater until the obstruction is corrected |
| Heater oversized for the space | Follow the manufacturer’s low-power and maintenance guidance |

## Maintenance and altitude kits

An approved altitude sensor or kit is generally preferable to manual trial-and-error because it is matched to the heater’s control logic. Keep the combustion air inlet and exhaust short, supported and free from snow, dust and insects. Follow the service interval for the burner screen, glow plug and fuel filter. Never share an exhaust path with a generator or engine, and never route exhaust beneath an opening where it can re-enter the vehicle.

## Sources and assumptions

Final pulse values, altitude limits, service intervals and installation clearances must come from the exact heater and controller documentation. The arithmetic example is illustrative only. This article does not certify a heater installation or authorize an ECU modification.
