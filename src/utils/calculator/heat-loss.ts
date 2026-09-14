export type HeatLossInput = {
  floorAreaM2: number;
  wallAreaM2: number;
  roofAreaM2: number;
  windowAreaM2: number;
  wallUValue: number;
  roofUValue: number;
  floorUValue: number;
  windowUValue: number;
  indoorTemperatureC: number;
  outdoorDesignTemperatureC: number;
  volumeM3: number;
  airChangesPerHour: number;
  internalGainsWatts: number;
  safetyFactor: number;
};

export function calculateHeatLoss(input: HeatLossInput) {
  const area = (value: number) => Math.max(0, value);
  const u = (value: number) => Math.max(0, value);
  const deltaT = Math.max(0, input.indoorTemperatureC - input.outdoorDesignTemperatureC);
  const transmissionWatts =
    area(input.wallAreaM2) * u(input.wallUValue) * deltaT +
    area(input.roofAreaM2) * u(input.roofUValue) * deltaT +
    area(input.floorAreaM2) * u(input.floorUValue) * deltaT +
    area(input.windowAreaM2) * u(input.windowUValue) * deltaT;
  const ventilationWatts = 0.33 * area(input.volumeM3) * area(input.airChangesPerHour) * deltaT;
  const netHeatLossWatts = Math.max(0, transmissionWatts + ventilationWatts - area(input.internalGainsWatts));
  const designHeatLoadWatts = netHeatLossWatts * Math.min(2, Math.max(1, input.safetyFactor));
  const warnings: string[] = [];

  if (!deltaT || !input.floorAreaM2 || !input.volumeM3) warnings.push("Enter the building geometry and design temperatures before relying on the estimate.");
  if (input.airChangesPerHour <= 0) warnings.push("Air changes must include intentional ventilation and infiltration; zero is not a realistic design assumption.");
  warnings.push("This is a screening estimate, not a Manual J or local HVAC design. A qualified designer must verify climate data, envelope details, ventilation, moisture and equipment operating limits.");

  return { deltaT, transmissionWatts, ventilationWatts, netHeatLossWatts, designHeatLoadWatts, designHeatLoadBtuPerHour: designHeatLoadWatts * 3.412, warnings };
}
