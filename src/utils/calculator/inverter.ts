export type InverterCalculationInput = {
  continuousLoadWatts: number;
  surgeLoadWatts: number;
  systemVoltage: number;
  inverterEfficiency: number;
  continuousMargin: number;
  surgeMargin: number;
  selectedContinuousWatts: number;
  selectedPeakWatts: number;
};

export type InverterCalculationResult = {
  recommendedContinuousWatts: number;
  recommendedPeakWatts: number;
  batteryContinuousCurrent: number;
  batteryPeakCurrent: number;
  continuousOk: boolean;
  peakOk: boolean;
};

const STANDARD_INVERTER_SIZES = [300, 500, 800, 1000, 1200, 1600, 2000, 2400, 3000, 4000, 5000];

export function calculateInverter(input: InverterCalculationInput): InverterCalculationResult {
  const systemVoltage = Math.max(0.1, input.systemVoltage);
  const continuousLoadWatts = Math.max(0, input.continuousLoadWatts);
  const surgeLoadWatts = Math.max(0, input.surgeLoadWatts);
  const efficiency = Math.min(Math.max(input.inverterEfficiency, 0.5), 1);
  const continuousTarget = continuousLoadWatts * Math.max(1, input.continuousMargin);
  const surgeTarget = surgeLoadWatts * Math.max(1, input.surgeMargin);
  const recommendedContinuousWatts = STANDARD_INVERTER_SIZES.find(size => size >= continuousTarget) ?? STANDARD_INVERTER_SIZES.at(-1)!;
  const recommendedPeakWatts = Math.max(recommendedContinuousWatts, Math.ceil(surgeTarget / 100) * 100);
  const batteryContinuousCurrent = continuousLoadWatts / (systemVoltage * efficiency);
  const batteryPeakCurrent = surgeLoadWatts / (systemVoltage * efficiency);

  return {
    recommendedContinuousWatts,
    recommendedPeakWatts,
    batteryContinuousCurrent,
    batteryPeakCurrent,
    continuousOk: input.selectedContinuousWatts >= continuousTarget,
    peakOk: input.selectedPeakWatts >= surgeTarget,
  };
}
