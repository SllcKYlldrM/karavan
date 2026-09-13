export type TowingCalculationInput = {
  vehicleKerbweightKg: number;
  vehicleTowingLimitKg: number;
  vehiclePayloadLimitKg: number;
  passengersAndLuggageKg: number;
  caravanMtplmKg: number;
  caravanActualWeightKg: number;
  noseWeightKg: number;
  towballLimitKg: number;
};

export function calculateTowing(input: TowingCalculationInput) {
  const vehicleKerbweightKg = Math.max(0, input.vehicleKerbweightKg);
  const vehicleTowingLimitKg = Math.max(0, input.vehicleTowingLimitKg);
  const vehiclePayloadLimitKg = Math.max(0, input.vehiclePayloadLimitKg);
  const passengersAndLuggageKg = Math.max(0, input.passengersAndLuggageKg);
  const caravanMtplmKg = Math.max(0, input.caravanMtplmKg);
  const caravanActualWeightKg = Math.max(0, input.caravanActualWeightKg);
  const noseWeightKg = Math.max(0, input.noseWeightKg);
  const towballLimitKg = Math.max(0, input.towballLimitKg);
  const ratio = vehicleKerbweightKg > 0 ? (caravanActualWeightKg / vehicleKerbweightKg) * 100 : 0;
  const towingMarginKg = vehicleTowingLimitKg - caravanActualWeightKg;
  const remainingPayloadKg = vehiclePayloadLimitKg - passengersAndLuggageKg - noseWeightKg;
  const noseWeightPercent = caravanActualWeightKg > 0 ? (noseWeightKg / caravanActualWeightKg) * 100 : 0;
  const mtplmMarginKg = caravanMtplmKg - caravanActualWeightKg;
  const warnings: string[] = [];

  if (!vehicleKerbweightKg || !vehicleTowingLimitKg || !vehiclePayloadLimitKg || !caravanActualWeightKg) {
    warnings.push("Enter the limits from the vehicle and caravan manufacturer documents before relying on the result.");
  }
  if (towingMarginKg < 0) warnings.push("The entered caravan mass exceeds the vehicle's stated braked towing limit.");
  if (caravanMtplmKg > 0 && caravanActualWeightKg > caravanMtplmKg) warnings.push("The entered actual caravan mass exceeds the caravan MTPLM.");
  if (remainingPayloadKg < 0) warnings.push("Passengers, luggage and nose weight exceed the vehicle payload allowance.");
  if (towballLimitKg > 0 && noseWeightKg > towballLimitKg) warnings.push("The entered nose weight exceeds the vehicle or towbar towball limit.");
  if (caravanActualWeightKg > 0 && (noseWeightPercent < 5 || noseWeightPercent > 7)) warnings.push("Nose-weight percentage is outside the common 5–7% planning range; verify the caravan and towbar manufacturer's limits.");
  if (ratio > 85) warnings.push("The 85% ratio is only a planning guideline, not a legal or universal safety limit. Check stability, loading, tyres, brakes, licence and local rules.");

  return {
    ratio,
    towingMarginKg,
    remainingPayloadKg,
    noseWeightPercent,
    mtplmMarginKg,
    warnings,
    limitsPass: warnings.length === 0,
  };
}
