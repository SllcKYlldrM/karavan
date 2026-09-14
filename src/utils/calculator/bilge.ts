export type BilgeInput = {
  pumpRatedFlowLitresPerMinute: number;
  flowDeratingPercent: number;
  pumpCount: number;
  pumpCurrentAmps: number;
  batteryCapacityAh: number;
  batteryUsableDepth: number;
  batteryVoltage: number;
  emergencyDurationHours: number;
};

export function calculateBilge(input: BilgeInput) {
  const flow = Math.max(0, input.pumpRatedFlowLitresPerMinute);
  const derating = Math.min(0.9, Math.max(0, input.flowDeratingPercent / 100));
  const pumpCount = Math.max(1, Math.floor(input.pumpCount));
  const current = Math.max(0, input.pumpCurrentAmps);
  const batteryAh = Math.max(0, input.batteryCapacityAh);
  const usableDepth = Math.min(1, Math.max(0.01, input.batteryUsableDepth));
  const batteryVoltage = Math.max(0.1, input.batteryVoltage);
  const effectiveFlowLitresPerMinute = flow * (1 - derating) * pumpCount;
  const totalCurrentAmps = current * pumpCount;
  const batteryRuntimeHours = totalCurrentAmps > 0 ? (batteryAh * usableDepth) / totalCurrentAmps : 0;
  const emergencyRuntimeHours = Math.min(batteryRuntimeHours, Math.max(0, input.emergencyDurationHours));
  const emergencyRemovalLitres = effectiveFlowLitresPerMinute * 60 * emergencyRuntimeHours;
  const warnings: string[] = [];

  if (!flow || !current || !batteryAh) warnings.push("Enter pump and battery datasheet values before relying on the emergency estimate.");
  warnings.push("Rated pump flow is not guaranteed at the installed head, hose length, wiring voltage or debris condition. Use the manufacturer's tested curve and provide independent high-water alarms and manual backup.");

  return { effectiveFlowLitresPerMinute, totalCurrentAmps, batteryRuntimeHours, emergencyRuntimeHours, emergencyRemovalLitres, batteryEnergyWh: batteryAh * batteryVoltage, warnings };
}
