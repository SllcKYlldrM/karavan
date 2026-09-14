export type RainwaterInput = {
  roofAreaM2: number;
  rainfallMm: number;
  runoffCoefficient: number;
  filterEfficiency: number;
  dailyDemandLitres: number;
  storageDays: number;
  tankCapacityLitres: number;
};

export function calculateRainwater(input: RainwaterInput) {
  const roofAreaM2 = Math.max(0, input.roofAreaM2);
  const rainfallMm = Math.max(0, input.rainfallMm);
  const runoffCoefficient = Math.min(1, Math.max(0, input.runoffCoefficient));
  const filterEfficiency = Math.min(1, Math.max(0, input.filterEfficiency));
  const dailyDemandLitres = Math.max(0, input.dailyDemandLitres);
  const storageDays = Math.max(0, input.storageDays);
  const capturedLitres = roofAreaM2 * rainfallMm * runoffCoefficient * filterEfficiency;
  const recommendedTankLitres = dailyDemandLitres * storageDays;
  const tankDays = dailyDemandLitres > 0 ? Math.max(0, input.tankCapacityLitres) / dailyDemandLitres : 0;
  const warnings: string[] = [];

  if (!roofAreaM2 || !rainfallMm || !dailyDemandLitres) warnings.push("Enter roof area, a measured design rainfall event and realistic daily demand.");
  warnings.push("Rainwater quality, first-flush diversion, potable treatment, overflow, local water rights and structural tank loads require separate design checks.");

  return { capturedLitres, recommendedTankLitres, tankDays, warnings };
}
