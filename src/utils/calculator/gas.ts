export type GasCalculationInput = {
  bottleCapacityKg: number;
  appliancePowerKw: number;
  appliancesInUse: number;
  hoursPerDay: number;
  efficiency: number;
  reserveFactor: number;
  energyPerKgKwh: number;
};

export function calculateGas(input: GasCalculationInput) {
  const bottleCapacityKg = Math.max(0, input.bottleCapacityKg);
  const appliancePowerKw = Math.max(0, input.appliancePowerKw);
  const appliancesInUse = Math.max(0, input.appliancesInUse);
  const hoursPerDay = Math.max(0, Math.min(24, input.hoursPerDay));
  const efficiency = Math.min(1, Math.max(0.01, input.efficiency));
  const reserveFactor = Math.min(1, Math.max(0, input.reserveFactor));
  const energyPerKgKwh = Math.max(0, input.energyPerKgKwh);
  const usableGasKg = bottleCapacityKg * (1 - reserveFactor);
  const usefulHeatPerKgKwh = energyPerKgKwh * efficiency;
  const totalPowerKw = appliancePowerKw * appliancesInUse;
  const runtimeHours = totalPowerKw > 0 && usefulHeatPerKgKwh > 0 ? (usableGasKg * usefulHeatPerKgKwh) / totalPowerKw : 0;
  const dailyEnergyKwh = totalPowerKw * hoursPerDay;
  const dailyGasKg = usefulHeatPerKgKwh > 0 ? dailyEnergyKwh / usefulHeatPerKgKwh : 0;
  const runtimeDays = hoursPerDay > 0 ? runtimeHours / hoursPerDay : 0;
  const warnings: string[] = [];

  if (!bottleCapacityKg || !appliancePowerKw || !energyPerKgKwh) warnings.push("Enter the bottle and appliance data from the cylinder label and manufacturer documentation.");
  if (efficiency < 0.7) warnings.push("The efficiency assumption is low; verify whether the appliance power rating is input fuel power or useful heat output.");
  if (input.hoursPerDay < 0 || input.hoursPerDay > 24) warnings.push("Daily operating time was clamped to the 0–24 hour range.");
  warnings.push("Never use this result to approve a gas installation. A qualified gas professional must verify regulators, hoses, ventilation, combustion air, exhaust and leak testing.");

  return { usableGasKg, usefulHeatPerKgKwh, totalPowerKw, runtimeHours, runtimeDays, dailyEnergyKwh, dailyGasKg, warnings };
}
