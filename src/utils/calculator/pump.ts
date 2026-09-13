export type PumpCalculationInput = {
  pumpFlowLitresPerMinute: number;
  peakDemandLitresPerMinute: number;
  dailyWaterUseLitres: number;
  accumulatorDrawdownLitres: number;
  pumpVoltage: number;
  pumpCurrentAmps: number;
};

export function calculatePump(input: PumpCalculationInput) {
  const pumpFlowLitresPerMinute = Math.max(0, input.pumpFlowLitresPerMinute);
  const peakDemandLitresPerMinute = Math.max(0, input.peakDemandLitresPerMinute);
  const dailyWaterUseLitres = Math.max(0, input.dailyWaterUseLitres);
  const accumulatorDrawdownLitres = Math.max(0, input.accumulatorDrawdownLitres);
  const pumpVoltage = Math.max(0, input.pumpVoltage);
  const pumpCurrentAmps = Math.max(0, input.pumpCurrentAmps);
  const dutyRatio = pumpFlowLitresPerMinute > 0 ? peakDemandLitresPerMinute / pumpFlowLitresPerMinute : 0;
  const dailyRuntimeMinutes = pumpFlowLitresPerMinute > 0 ? dailyWaterUseLitres / pumpFlowLitresPerMinute : 0;
  const estimatedStartsPerDay = accumulatorDrawdownLitres > 0 ? dailyWaterUseLitres / accumulatorDrawdownLitres : 0;
  const dailyElectricalAh = (dailyRuntimeMinutes / 60) * pumpCurrentAmps;
  const dailyElectricalWh = dailyElectricalAh * pumpVoltage;
  const warnings: string[] = [];

  if (!pumpFlowLitresPerMinute || !dailyWaterUseLitres) warnings.push("Enter the pump datasheet flow and a realistic measured or estimated daily water use.");
  if (dutyRatio > 1) warnings.push("Peak demand exceeds the entered pump flow; pressure and flow will fall until demand is reduced or a larger pump is selected.");
  if (dutyRatio > 0.7 && dutyRatio <= 1) warnings.push("The estimated peak duty is high; verify the pump's permitted duty cycle and cooling requirements.");
  if (!accumulatorDrawdownLitres) warnings.push("Enter the measured accumulator drawdown volume to estimate pump starts; nominal tank volume is not the same as drawdown volume.");
  warnings.push("Set accumulator pre-charge and pressure-switch limits from the pump and tank manufacturer's instructions. Protect the pump with the specified fuse and never run it dry.");

  return { dutyRatio, dailyRuntimeMinutes, estimatedStartsPerDay, dailyElectricalAh, dailyElectricalWh, warnings };
}
