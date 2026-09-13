export type CableCalculationInput = {
  systemVoltage: number;
  currentAmps: number;
  lengthOneWay: number;
  maxVoltageDrop: number;
  cableAmpacity: number;
  existingFuseAmps: number;
  continuousFactor: number;
};

export type CableCalculationResult = {
  loopLength: number;
  exactCableArea: number;
  recommendedCableArea: number;
  voltageDrop: number;
  minimumAmpacity: number;
  minimumFuseAmps: number;
  maximumFuseAmps: number;
  fuseSelectionPossible: boolean;
  voltageDropOk: boolean;
  ampacityOk: boolean;
  fuseOk: boolean;
};

const COPPER_RESISTIVITY = 0.0175;
const STANDARD_CABLE_SIZES = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240];
const STANDARD_FUSES = [5, 7.5, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100, 125, 150, 175, 200, 250, 300, 400, 500];

export function calculateCable(input: CableCalculationInput): CableCalculationResult {
  const systemVoltage = Math.max(0.1, input.systemVoltage);
  const currentAmps = Math.max(0, input.currentAmps);
  const maxVoltageDrop = Math.min(1, Math.max(0.001, input.maxVoltageDrop));
  const continuousFactor = Math.max(1, input.continuousFactor);
  const loopLength = Math.max(0, input.lengthOneWay) * 2;
  const allowedDropVolts = Math.max(0.001, systemVoltage * maxVoltageDrop);
  const exactCableArea = (COPPER_RESISTIVITY * loopLength * currentAmps) / allowedDropVolts;
  const recommendedCableArea = STANDARD_CABLE_SIZES.find(size => size >= exactCableArea) ?? STANDARD_CABLE_SIZES.at(-1)!;
  const voltageDrop = currentAmps > 0
    ? ((COPPER_RESISTIVITY * loopLength * currentAmps) / (recommendedCableArea * systemVoltage)) * 100
    : 0;
  const minimumAmpacity = currentAmps * continuousFactor;
  const minimumFuseAmps = STANDARD_FUSES.find(size => size >= minimumAmpacity) ?? STANDARD_FUSES.at(-1)!;
  const compatibleFuses = STANDARD_FUSES.filter(size => size <= input.cableAmpacity);
  const maximumFuseAmps = compatibleFuses.at(-1) ?? 0;
  const fuseSelectionPossible = minimumFuseAmps <= maximumFuseAmps;

  return {
    loopLength,
    exactCableArea,
    recommendedCableArea,
    voltageDrop,
    minimumAmpacity,
    minimumFuseAmps,
    maximumFuseAmps,
    fuseSelectionPossible,
    voltageDropOk: voltageDrop <= maxVoltageDrop * 100,
    ampacityOk: Math.max(0, input.cableAmpacity) >= minimumAmpacity,
    fuseOk: fuseSelectionPossible && (input.existingFuseAmps <= 0 || (input.existingFuseAmps >= minimumFuseAmps && input.existingFuseAmps <= maximumFuseAmps)),
  };
}
