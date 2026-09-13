export type WeightCalculationInput = {
  caravanUnladenMassKg: number;
  caravanMtplmKg: number;
  cargoAndWaterKg: number;
  noseWeightKg: number;
  noseWeightLimitKg: number;
  axleGroupLimitKg: number;
};

export function calculateWeight(input: WeightCalculationInput) {
  const caravanUnladenMassKg = Math.max(0, input.caravanUnladenMassKg);
  const caravanMtplmKg = Math.max(0, input.caravanMtplmKg);
  const cargoAndWaterKg = Math.max(0, input.cargoAndWaterKg);
  const noseWeightKg = Math.max(0, input.noseWeightKg);
  const noseWeightLimitKg = Math.max(0, input.noseWeightLimitKg);
  const axleGroupLimitKg = Math.max(0, input.axleGroupLimitKg);
  const loadedMassKg = caravanUnladenMassKg + cargoAndWaterKg;
  const remainingPayloadKg = caravanMtplmKg - loadedMassKg;
  const estimatedAxleGroupLoadKg = Math.max(0, loadedMassKg - noseWeightKg);
  const noseWeightPercent = loadedMassKg > 0 ? (noseWeightKg / loadedMassKg) * 100 : 0;
  const warnings: string[] = [];

  if (!caravanMtplmKg || !caravanUnladenMassKg) warnings.push("Enter the mass values from the caravan plate and manufacturer documents.");
  if (remainingPayloadKg < 0) warnings.push("The estimated loaded mass exceeds the caravan MTPLM.");
  if (noseWeightLimitKg > 0 && noseWeightKg > noseWeightLimitKg) warnings.push("The entered nose weight exceeds the towbar or vehicle limit.");
  if (axleGroupLimitKg > 0 && estimatedAxleGroupLoadKg > axleGroupLimitKg) warnings.push("The estimated axle-group load exceeds the entered limit.");
  if (noseWeightPercent < 5 || noseWeightPercent > 7) warnings.push("Nose-weight percentage is outside a common planning range; verify the caravan manufacturer's loading guidance.");
  warnings.push("This is not an axle-by-axle approval. Weigh the loaded caravan, nose and tow vehicle at a certified weighbridge and check each manufacturer's limit.");

  return { loadedMassKg, remainingPayloadKg, estimatedAxleGroupLoadKg, noseWeightPercent, warnings };
}
