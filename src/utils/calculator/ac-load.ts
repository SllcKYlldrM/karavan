export type AcLoadCalculationInput = {
  systemVoltage: number;
  continuousLoadWatts: number;
  largestStartupWatts: number;
  otherStartupWatts: number;
  powerFactor: number;
  marginFactor: number;
  breakerAmps: number;
};

export function calculateAcLoad(input: AcLoadCalculationInput) {
  const systemVoltage = Math.max(0, input.systemVoltage);
  const continuousLoadWatts = Math.max(0, input.continuousLoadWatts);
  const largestStartupWatts = Math.max(0, input.largestStartupWatts);
  const otherStartupWatts = Math.max(0, input.otherStartupWatts);
  const powerFactor = Math.min(1, Math.max(0.1, input.powerFactor));
  const marginFactor = Math.min(2, Math.max(1, input.marginFactor));
  const breakerAmps = Math.max(0, input.breakerAmps);
  const continuousCurrentAmps = systemVoltage > 0 ? continuousLoadWatts / (systemVoltage * powerFactor) : 0;
  const startupLoadWatts = continuousLoadWatts + largestStartupWatts + otherStartupWatts;
  const startupCurrentAmps = systemVoltage > 0 ? startupLoadWatts / (systemVoltage * powerFactor) : 0;
  const recommendedSourceVa = startupLoadWatts * marginFactor / powerFactor;
  const breakerMarginAmps = breakerAmps - continuousCurrentAmps;
  const warnings: string[] = [];

  if (!systemVoltage || !continuousLoadWatts) warnings.push("Enter the measured or nameplate values for the supply and connected loads.");
  if (startupCurrentAmps > breakerAmps && breakerAmps > 0) warnings.push("Estimated startup current exceeds the entered breaker rating; verify inrush current, circuit protection and load-shedding behavior.");
  if (continuousCurrentAmps > breakerAmps * 0.8 && breakerAmps > 0) warnings.push("Continuous current is above an 80% planning threshold; confirm local code and breaker loading rules with a qualified electrician.");
  if (largestStartupWatts > continuousLoadWatts * 3) warnings.push("The entered startup load is unusually high compared with the continuous load; verify the appliance datasheet or measured inrush.");
  warnings.push("This is a planning estimate. Shore-power polarity, RCD/GFCI, earthing, cable rating, transfer switching and generator neutral bonding require qualified inspection.");

  return { continuousCurrentAmps, startupLoadWatts, startupCurrentAmps, recommendedSourceVa, breakerMarginAmps, warnings };
}
