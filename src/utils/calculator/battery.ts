export type BatteryCalculationInput = {
  dailyWh: number;
  systemVoltage: number;
  autonomyDays: number;
  usableDepthOfDischarge: number;
  batteryCapacityAh: number;
  batteryNominalVoltage: number;
  batteryCount: number;
  temperatureFactor: number;
};

export type BatteryCalculationResult = {
  requiredBankAh: number;
  recommendedBatteryCount: number;
  configuredBankAh: number;
  nominalBankWh: number;
  usableBankWh: number;
  voltageOk: boolean;
  capacityOk: boolean;
};

export function calculateBatteryBank(input: BatteryCalculationInput): BatteryCalculationResult {
  const systemVoltage = Math.max(0.1, input.systemVoltage);
  const batteryCapacityAh = Math.max(0.1, input.batteryCapacityAh);
  const batteryNominalVoltage = Math.max(0.1, input.batteryNominalVoltage);
  const batteryCount = Math.max(0, input.batteryCount);
  const autonomyDays = Math.max(0, input.autonomyDays);
  const dailyWh = Math.max(0, input.dailyWh);
  const safeDod = Math.min(Math.max(input.usableDepthOfDischarge, 0.01), 1);
  const safeTemperatureFactor = Math.min(Math.max(input.temperatureFactor, 0.5), 1);
  const seriesBatteryCount = Math.max(1, Math.ceil(systemVoltage / batteryNominalVoltage));
  const completeParallelStrings = Math.floor(batteryCount / seriesBatteryCount);
  const requiredBankAh = dailyWh * autonomyDays / (systemVoltage * safeDod * safeTemperatureFactor);
  const recommendedBatteryCount = Math.max(1, seriesBatteryCount * Math.ceil(requiredBankAh / batteryCapacityAh));
  const configuredBankAh = batteryCapacityAh * completeParallelStrings;
  const nominalBankWh = configuredBankAh * systemVoltage;
  const usableBankWh = nominalBankWh * safeDod * safeTemperatureFactor;

  return {
    requiredBankAh,
    recommendedBatteryCount,
    configuredBankAh,
    nominalBankWh,
    usableBankWh,
    voltageOk: Math.abs(systemVoltage - batteryNominalVoltage * seriesBatteryCount) <= 1,
    capacityOk: configuredBankAh >= requiredBankAh,
  };
}
