export type CalculatorLink = {
  title: string;
  href: string;
  guideTitle: string;
  guideHref: string;
  nextTitle: string;
  nextHref: string;
};

export const calculatorLinks: Record<string, CalculatorLink> = {
  "system-planner": { title: "Complete off-grid system planner", href: "/tools/system-planner/", guideTitle: "Off-grid caravan solar power setup guide", guideHref: "/posts/off-grid-caravan-solar-power-setup-guide/", nextTitle: "Review battery capacity", nextHref: "/tools/battery-calculator/" },
  "solar-system": { title: "Solar and battery calculator", href: "/tools/solar-calculator/", guideTitle: "Off-grid caravan solar power setup guide", guideHref: "/posts/off-grid-caravan-solar-power-setup-guide/", nextTitle: "Check battery capacity", nextHref: "/tools/battery-calculator/" },
  "battery-sizing": { title: "Battery bank calculator", href: "/tools/battery-calculator/", guideTitle: "LiFePO4 low-temperature protection guide", guideHref: "/posts/lifepo4-low-temperature-protection-thermal-pad-heating-circuit/", nextTitle: "Size the inverter", nextHref: "/tools/inverter-calculator/" },
  "cable-sizing": { title: "Cable and fuse calculator", href: "/tools/cable-calculator/", guideTitle: "Caravan 12V cable size and voltage drop guide", guideHref: "/posts/caravan-12v-cable-size-voltage-drop-calculator/", nextTitle: "Review inverter load", nextHref: "/tools/inverter-calculator/" },
  "inverter-sizing": { title: "Inverter sizing calculator", href: "/tools/inverter-calculator/", guideTitle: "Eliminating inverter idle power loss", guideHref: "/posts/eliminating-inverter-idle-loss-load-sensing-remote-switch-caravan/", nextTitle: "Check cable and fuse sizing", nextHref: "/tools/cable-calculator/" },
  "towing-safety": { title: "Towing and payload calculator", href: "/tools/towing-calculator/", guideTitle: "Caravan towing ratio and safety guide", guideHref: "/posts/caravan-towing-weight-ratio-calculator-safety-guide/", nextTitle: "Review payload distribution", nextHref: "/tools/weight-calculator/" },
  "heater-runtime": { title: "Heater runtime calculator", href: "/tools/heater-calculator/", guideTitle: "Diesel heater high-altitude calibration guide", guideHref: "/posts/diesel-heater-high-altitude-ecu-pulse-frequency-air-fuel-mixture/", nextTitle: "Estimate electrical load", nextHref: "/tools/battery-calculator/" },
  "gas-runtime": { title: "LPG runtime calculator", href: "/tools/gas-calculator/", guideTitle: "RV gas leak security and alarm systems", guideHref: "/posts/esp32-smart-rv-gas-leak-security-alarm-mqtt/", nextTitle: "Review heating demand", nextHref: "/tools/heater-calculator/" },
  "ac-load": { title: "AC load calculator", href: "/tools/ac-load-calculator/", guideTitle: "ESP32 RV AC shore-power load shedding", guideHref: "/posts/esp32-rv-ac-shore-power-smart-load-shedder-modbus-mqtt/", nextTitle: "Size the inverter", nextHref: "/tools/inverter-calculator/" },
  "pump-sizing": { title: "Water pump calculator", href: "/tools/pump-calculator/", guideTitle: "12V RV water pump and accumulator sizing", guideHref: "/posts/rv-12v-water-pump-accumulator-tank-sizing-pressure-switch-calibration/", nextTitle: "Estimate water autonomy", nextHref: "/tools/water-calculator/" },
  "weight-sizing": { title: "Payload and weight calculator", href: "/tools/weight-calculator/", guideTitle: "Caravan weight distribution guide", guideHref: "/posts/caravan-weight-distribution-guide/", nextTitle: "Check towing margins", nextHref: "/tools/towing-calculator/" },
  "water-sizing": { title: "Water autonomy calculator", href: "/tools/water-calculator/", guideTitle: "Non-contact RV tank-level monitoring", guideHref: "/posts/esp32-non-contact-capacitive-rv-tank-level-monitoring-mqtt/", nextTitle: "Size the water pump", nextHref: "/tools/pump-calculator/" },
  "dc-dc-sizing": { title: "DC-DC charger calculator", href: "/tools/dc-dc-calculator/", guideTitle: "Off-grid caravan DC-DC charger wiring guide", guideHref: "/posts/off-grid-caravan-dc-dc-charger-efficiency-wiring-grounding/", nextTitle: "Check battery capacity", nextHref: "/tools/battery-calculator/" },
  "bilge-sizing": { title: "Bilge pump calculator", href: "/tools/bilge-calculator/", guideTitle: "Marine bilge and pump planning", guideHref: "/scopes/marine-boat-systems/bilge-and-pumps/", nextTitle: "Review battery runtime", nextHref: "/tools/battery-calculator/" },
  "heat-loss": { title: "Tiny house heat-loss calculator", href: "/tools/heat-loss-calculator/", guideTitle: "Tiny house heating systems", guideHref: "/scopes/tiny-house-systems/heating/", nextTitle: "Review ventilation planning", nextHref: "/scopes/tiny-house-systems/cooling-and-ventilation/" },
  "rainwater-sizing": { title: "Rainwater harvesting calculator", href: "/tools/rainwater-calculator/", guideTitle: "Tiny house freshwater systems", guideHref: "/scopes/tiny-house-systems/freshwater/", nextTitle: "Review wastewater planning", nextHref: "/scopes/tiny-house-systems/wastewater-and-treatment/" },
};
