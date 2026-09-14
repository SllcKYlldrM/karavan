export type SolarPanelPreset = {
  id: string;
  name: string;
  watts: number;
  voc: number;
  isc: number;
};

export type MpptPreset = {
  id: string;
  name: string;
  maxPvVoltage: number;
  maxPvShortCircuitCurrent: number;
  chargeCurrent: number;
  sourceUrl: string;
};

export type BatteryPreset = {
  id: string;
  name: string;
  nominalVoltage: number;
  capacityAh: number;
  maxContinuousDischarge: number;
  usableDepthOfDischarge: number;
  sourceUrl: string;
};

export type InverterPreset = {
  id: string;
  name: string;
  nominalVoltage: number;
  continuousWatts: number;
  peakWatts: number;
  efficiency: number;
  sourceUrl: string;
};

export const solarPanelPresets: SolarPanelPreset[] = [
  { id: "generic-200w", name: "Generic 200W RV panel", watts: 200, voc: 24, isc: 10.5 },
  { id: "generic-100w", name: "Generic 100W RV panel", watts: 100, voc: 22, isc: 6 },
  { id: "custom-panel", name: "Custom panel — enter datasheet values", watts: 200, voc: 24, isc: 10.5 },
];

export const mpptPresets: MpptPreset[] = [
  {
    id: "victron-75-15",
    name: "Victron SmartSolar MPPT 75/15",
    maxPvVoltage: 75,
    maxPvShortCircuitCurrent: 15,
    chargeCurrent: 15,
    sourceUrl: "https://www.victronenergy.com/media/pg/Manual_SmartSolar_MPPT_75-10_up_to_100-20/en/technical-specifications.html",
  },
  {
    id: "victron-100-30",
    name: "Victron SmartSolar MPPT 100/30",
    maxPvVoltage: 100,
    maxPvShortCircuitCurrent: 35,
    chargeCurrent: 30,
    sourceUrl: "https://www.victronenergy.com/media/pg/Manual_SmartSolar_MPPT_100-30__100-50/en/technical-specifications.html",
  },
  {
    id: "victron-100-15",
    name: "Victron SmartSolar MPPT 100/15",
    maxPvVoltage: 100,
    maxPvShortCircuitCurrent: 15,
    chargeCurrent: 15,
    sourceUrl: "https://www.victronenergy.com/media/pg/Manual_SmartSolar_MPPT_75-10_up_to_100-20/en/technical-specifications.html",
  },
  {
    id: "victron-100-20",
    name: "Victron SmartSolar MPPT 100/20",
    maxPvVoltage: 100,
    maxPvShortCircuitCurrent: 20,
    chargeCurrent: 20,
    sourceUrl: "https://www.victronenergy.com/media/pg/Manual_SmartSolar_MPPT_75-10_up_to_100-20/en/technical-specifications.html",
  },
  {
    id: "victron-100-50",
    name: "Victron SmartSolar MPPT 100/50",
    maxPvVoltage: 100,
    maxPvShortCircuitCurrent: 60,
    chargeCurrent: 50,
    sourceUrl: "https://www.victronenergy.com/media/pg/Manual_SmartSolar_MPPT_100-30__100-50/en/technical-specifications.html",
  },
  {
    id: "custom-mppt",
    name: "Custom MPPT — enter datasheet limits",
    maxPvVoltage: 100,
    maxPvShortCircuitCurrent: 35,
    chargeCurrent: 30,
    sourceUrl: "",
  },
];

export const batteryPresets: BatteryPreset[] = [
  {
    id: "victron-lithium-12-8-200",
    name: "Victron Lithium Smart 12.8V/200Ah",
    nominalVoltage: 12.8,
    capacityAh: 200,
    maxContinuousDischarge: 400,
    usableDepthOfDischarge: 0.8,
    sourceUrl: "https://www.victronenergy.com/media/pg/Lithium_Battery_Smart/en/technical-data.html",
  },
  {
    id: "generic-lifepo4-100",
    name: "Generic LiFePO4 12V/100Ah — illustrative value; verify datasheet",
    nominalVoltage: 12.8,
    capacityAh: 100,
    maxContinuousDischarge: 100,
    usableDepthOfDischarge: 0.8,
    sourceUrl: "",
  },
  {
    id: "custom-battery",
    name: "Custom battery — enter datasheet limits",
    nominalVoltage: 12.8,
    capacityAh: 100,
    maxContinuousDischarge: 100,
    usableDepthOfDischarge: 0.8,
    sourceUrl: "",
  },
];

export const inverterPresets: InverterPreset[] = [
  {
    id: "victron-multiplus-12-2000",
    name: "Victron MultiPlus 12/2000/80",
    nominalVoltage: 12,
    continuousWatts: 1600,
    peakWatts: 3500,
    efficiency: 0.93,
    sourceUrl: "https://www.victronenergy.com/media/pg/MultiPlus_2kVA_230V/en/technical-data-2kva.html",
  },
  {
    id: "custom-inverter",
    name: "Custom inverter — enter datasheet limits",
    nominalVoltage: 12,
    continuousWatts: 1000,
    peakWatts: 2000,
    efficiency: 0.9,
    sourceUrl: "",
  },
];
