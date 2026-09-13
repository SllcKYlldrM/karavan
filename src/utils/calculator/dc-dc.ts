import { calculateCable } from "@/utils/calculator/cable";

export type DcDcPreset = {
  id: string;
  name: string;
  outputAmps: number;
  efficiency: number;
  sourceUrl: string;
};

export const dcDcPresets: DcDcPreset[] = [
  { id: "victron-orion-xs-50", name: "Victron Orion XS 12/12-50A", outputAmps: 50, efficiency: 0.985, sourceUrl: "https://www.victronenergy.com/media/pg/Orion_XS_12-12-50A_DC-DC_battery_charger/en/technical-data.html" },
  { id: "victron-orion-xs-70", name: "Victron Orion XS 12/12-70A", outputAmps: 70, efficiency: 0.985, sourceUrl: "https://www.victronenergy.com/media/pg/Orion_XS_12-12-70A_DC-DC_Battery_Charger/en/technical-data.html" },
  { id: "custom-dc-dc", name: "Custom charger — enter datasheet values", outputAmps: 30, efficiency: 0.9, sourceUrl: "" },
];

export type DcDcCalculationInput = {
  batteryVoltage: number;
  alternatorVoltage: number;
  chargerOutputAmps: number;
  chargerEfficiency: number;
  drivingHours: number;
  alternatorRatedAmps: number;
  vehicleBaseLoadAmps: number;
  alternatorReserveFactor: number;
  cableLengthOneWay: number;
  maxVoltageDrop: number;
  cableAmpacity: number;
  existingInputFuseAmps: number;
};

export type DcDcCalculationResult = {
  inputCurrentAmps: number;
  availableAlternatorAmps: number;
  reservedAlternatorAmps: number;
  maximumSafeOutputAmps: number;
  dailyChargeAh: number;
  dailyChargeWh: number;
  inputCableArea: number;
  outputCableArea: number;
  inputFuseAmps: number;
  outputFuseAmps: number;
  alternatorOk: boolean;
  cableAmpacityOk: boolean;
  fuseOk: boolean;
};

const STANDARD_FUSES = [5, 7.5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 100, 125, 150, 175, 200];

const nextFuse = (amps: number) => STANDARD_FUSES.find(size => size >= amps) ?? STANDARD_FUSES.at(-1)!;

export function calculateDcDc(input: DcDcCalculationInput): DcDcCalculationResult {
  const batteryVoltage = Math.max(0.1, input.batteryVoltage);
  const alternatorVoltage = Math.max(0.1, input.alternatorVoltage);
  const chargerOutputAmps = Math.max(0, input.chargerOutputAmps);
  const efficiency = Math.min(Math.max(input.chargerEfficiency, 0.5), 1);
  const reserveFactor = Math.min(Math.max(input.alternatorReserveFactor, 0.5), 1);
  const availableAlternatorAmps = Math.max(0, input.alternatorRatedAmps - input.vehicleBaseLoadAmps);
  const reservedAlternatorAmps = availableAlternatorAmps * reserveFactor;
  const inputCurrentAmps = chargerOutputAmps * batteryVoltage / (alternatorVoltage * efficiency);
  const maximumSafeOutputAmps = reservedAlternatorAmps * alternatorVoltage * efficiency / batteryVoltage;
  const inputCable = calculateCable({ systemVoltage: alternatorVoltage, currentAmps: inputCurrentAmps, lengthOneWay: input.cableLengthOneWay, maxVoltageDrop: input.maxVoltageDrop, cableAmpacity: input.cableAmpacity, existingFuseAmps: input.existingInputFuseAmps, continuousFactor: 1.25 });
  const outputCable = calculateCable({ systemVoltage: batteryVoltage, currentAmps: chargerOutputAmps, lengthOneWay: input.cableLengthOneWay, maxVoltageDrop: input.maxVoltageDrop, cableAmpacity: input.cableAmpacity, existingFuseAmps: 0, continuousFactor: 1.25 });
  const inputFuseAmps = nextFuse(inputCurrentAmps * 1.25);
  const outputFuseAmps = nextFuse(chargerOutputAmps * 1.25);

  return {
    inputCurrentAmps,
    availableAlternatorAmps,
    reservedAlternatorAmps,
    maximumSafeOutputAmps,
    dailyChargeAh: chargerOutputAmps * Math.max(0, input.drivingHours),
    dailyChargeWh: chargerOutputAmps * batteryVoltage * Math.max(0, input.drivingHours),
    inputCableArea: inputCable.recommendedCableArea,
    outputCableArea: outputCable.recommendedCableArea,
    inputFuseAmps,
    outputFuseAmps,
    alternatorOk: inputCurrentAmps <= reservedAlternatorAmps,
    cableAmpacityOk: inputCable.ampacityOk && outputCable.ampacityOk,
    fuseOk: inputFuseAmps <= input.cableAmpacity && outputFuseAmps <= input.cableAmpacity,
  };
}
