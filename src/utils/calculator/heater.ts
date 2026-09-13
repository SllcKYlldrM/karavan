export type HeaterCalculationInput = {
  tankCapacityLitres: number;
  fuelBurnLitresPerHour: number;
  hoursPerDay: number;
  reserveFactor: number;
  heaterCurrentAmps: number;
  heaterVoltage: number;
};

export function calculateHeater(input: HeaterCalculationInput) {
  const tankCapacityLitres = Math.max(0, input.tankCapacityLitres);
  const fuelBurnLitresPerHour = Math.max(0, input.fuelBurnLitresPerHour);
  const hoursPerDay = Math.max(0, Math.min(24, input.hoursPerDay));
  const reserveFactor = Math.min(1, Math.max(0, input.reserveFactor));
  const heaterCurrentAmps = Math.max(0, input.heaterCurrentAmps);
  const heaterVoltage = Math.max(0, input.heaterVoltage);
  const usableFuelLitres = tankCapacityLitres * (1 - reserveFactor);
  const runtimeHours = fuelBurnLitresPerHour > 0 ? usableFuelLitres / fuelBurnLitresPerHour : 0;
  const runtimeDays = hoursPerDay > 0 ? runtimeHours / hoursPerDay : 0;
  const dailyFuelLitres = fuelBurnLitresPerHour * hoursPerDay;
  const dailyElectricalAh = heaterCurrentAmps * hoursPerDay;
  const dailyElectricalWh = dailyElectricalAh * heaterVoltage;
  const warnings: string[] = [];

  if (!fuelBurnLitresPerHour) warnings.push("Enter the heater's measured or manufacturer-rated fuel burn before relying on the runtime estimate.");
  if (input.hoursPerDay < 0 || input.hoursPerDay > 24) warnings.push("Hours per day was clamped to the 0–24 hour range.");
  if (reserveFactor < 0.1) warnings.push("A low reserve leaves little allowance for unusable fuel, cold starts and measurement error.");
  if (heaterCurrentAmps > 0 && heaterVoltage <= 0) warnings.push("Enter a valid 12V or 24V electrical system voltage for the electrical estimate.");

  return { usableFuelLitres, runtimeHours, runtimeDays, dailyFuelLitres, dailyElectricalAh, dailyElectricalWh, warnings };
}
