export type SolarLoad = {
  watts: number;
  quantity: number;
  hours: number;
  isAc?: boolean;
};

export type SolarCalculationInput = {
  loads: SolarLoad[];
  systemVoltage: number;
  autonomyDays: number;
  usableDepthOfDischarge: number;
  sunHours: number;
  systemEfficiency: number;
  cableLength: number;
  maxVoltageDrop: number;
  inverterEfficiency: number;
  panelWatts: number;
  panelVoc: number;
  panelIsc: number;
  panelCount: number;
  panelsInSeries: number;
  mpptMaxPvVoltage: number;
  mpptMaxPvShortCircuitCurrent: number;
  mpptChargeCurrent: number;
  coldVocMultiplier: number;
  batteryCapacityAh: number;
  batteryMaxContinuousDischarge: number;
  batteryCount: number;
  batteryNominalVoltage: number;
  inverterContinuousWatts: number;
  inverterPeakWatts: number;
  inverterNominalVoltage: number;
  dcDcChargerAmps: number;
  drivingHours: number;
  alternatorSpareAmps: number;
  dcDcEfficiency: number;
  shoreChargerAmps: number;
  shoreChargingHours: number;
  shoreChargingEfficiency: number;
};

export type SolarCalculationResult = {
  dailyWh: number;
  dailyDcWh: number;
  dailyAcWh: number;
  batteryAh: number;
  panelWatts: number;
  solarRequiredWh: number;
  dcDcChargingWh: number;
  shoreChargingWh: number;
  totalExternalChargingWh: number;
  dcDcAlternatorOk: boolean;
  maxLoadWatts: number;
  maxCurrent: number;
  inverterWatts: number;
  mpptCurrent: number;
  mpptAmps: number;
  mpptFuseAmps: number;
  arrayWatts: number;
  arrayVoc: number;
  arrayIsc: number;
  coldArrayVoc: number;
  seriesCount: number;
  parallelCount: number;
  mpptVoltageOk: boolean;
  mpptCurrentOk: boolean;
  mpptChargeCurrentOk: boolean;
  batteryCurrent: number;
  requiredBatteryAmpacity: number;
  recommendedFuseAmps: number;
  batteryCapacityOk: boolean;
  batteryVoltageOk: boolean;
  inverterVoltageOk: boolean;
  inverterPeakOk: boolean;
  systemLevels: {
    minimum: { batteryAh: number; panelWatts: number };
    balanced: { batteryAh: number; panelWatts: number };
    expandable: { batteryAh: number; panelWatts: number };
  };
  voltageDrop: number;
  cableArea: number;
};

const COPPER_RESISTIVITY = 0.0175;
const STANDARD_CABLE_SIZES = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240];

export function calculateSolarSystem(input: SolarCalculationInput): SolarCalculationResult {
  const systemVoltage = Math.max(0.1, input.systemVoltage);
  const batteryMaxContinuousDischarge = Math.max(0, input.batteryMaxContinuousDischarge);
  const batteryCount = Math.max(0, Math.floor(input.batteryCount));
  const panelCount = Math.max(0, Math.floor(input.panelCount));
  const panelWattsInput = Math.max(0, input.panelWatts);
  const panelVoc = Math.max(0, input.panelVoc);
  const panelIsc = Math.max(0, input.panelIsc);
  const usableDepthOfDischarge = Math.min(1, Math.max(0.01, input.usableDepthOfDischarge));
  const inverterEfficiency = Math.min(1, Math.max(0.5, input.inverterEfficiency));
  const sunHours = Math.max(0.1, input.sunHours);
  const systemEfficiency = Math.min(1, Math.max(0.1, input.systemEfficiency));
  const batteryVoltage = Math.max(0.1, input.batteryNominalVoltage || systemVoltage);
  const batterySeriesCount = Math.max(1, Math.ceil(systemVoltage / batteryVoltage));
  const batteryParallelCount = Math.floor(batteryCount / batterySeriesCount);
  const dailyDcWh = input.loads.reduce((total, load) => {
    const deviceWh = load.watts * load.quantity * load.hours;
    return total + (load.isAc ? 0 : deviceWh);
  }, 0);
  const dailyAcWh = input.loads.reduce((total, load) => {
    const deviceWh = load.watts * load.quantity * load.hours;
    return total + (load.isAc ? deviceWh / inverterEfficiency : 0);
  }, 0);
  const dailyWh = dailyDcWh + dailyAcWh;

  const batteryAh = dailyWh * Math.max(0, input.autonomyDays) / (systemVoltage * usableDepthOfDischarge);
  const dcDcChargingWh = Math.max(0, input.dcDcChargerAmps) * batteryVoltage * Math.max(0, input.drivingHours) * Math.min(1, Math.max(0, input.dcDcEfficiency));
  const shoreChargingWh = Math.max(0, input.shoreChargerAmps) * batteryVoltage * Math.max(0, input.shoreChargingHours) * Math.min(1, Math.max(0, input.shoreChargingEfficiency));
  const totalExternalChargingWh = dcDcChargingWh + shoreChargingWh;
  const solarRequiredWh = Math.max(0, dailyWh - totalExternalChargingWh);
  const panelWatts = solarRequiredWh / (sunHours * systemEfficiency);
  const dcDcAlternatorOk = input.dcDcChargerAmps <= input.alternatorSpareAmps;
  const arrayWatts = panelWattsInput * panelCount;
  const seriesCount = panelCount > 0 ? Math.max(1, Math.min(panelCount, Math.round(input.panelsInSeries))) : 0;
  const parallelCount = seriesCount > 0 ? Math.ceil(panelCount / seriesCount) : 0;
  const arrayVoc = panelVoc * seriesCount;
  const arrayIsc = panelIsc * parallelCount;
  const coldArrayVoc = arrayVoc * Math.max(1, input.coldVocMultiplier);
  const mpptVoltageOk = panelCount > 0 && coldArrayVoc <= Math.max(0, input.mpptMaxPvVoltage);
  const mpptCurrentOk = panelCount > 0 && arrayIsc <= Math.max(0, input.mpptMaxPvShortCircuitCurrent);
  const maxLoadWatts = Math.max(
    ...input.loads.map(load => load.watts * load.quantity / (load.isAc ? inverterEfficiency : 1)),
    0
  );
  const maxCurrent = maxLoadWatts / systemVoltage;
  const inverterWatts = Math.ceil((maxLoadWatts * 1.25) / 100) * 100;
  const mpptCurrent = arrayWatts / batteryVoltage;
  const MPPT_SIZES = [10, 15, 20, 30, 40, 50, 60, 70, 80, 100, 150];
  const mpptAmps = MPPT_SIZES.find(size => size >= mpptCurrent * 1.25) ?? MPPT_SIZES.at(-1)!;
  const mpptFuseAmps = Math.ceil((mpptAmps * 1.25) / 5) * 5;
  const mpptChargeCurrentOk = mpptAmps <= input.mpptChargeCurrent;
  const batteryCurrent = Math.max(0, input.inverterContinuousWatts) / (systemVoltage * inverterEfficiency);
  const requiredBatteryAmpacity = Math.max(maxCurrent, batteryCurrent) * 1.25;
  const FUSE_SIZES = [15, 20, 25, 30, 40, 50, 60, 80, 100, 125, 150, 175, 200, 250, 300, 400];
  const recommendedFuseAmps = FUSE_SIZES.find(size => size >= requiredBatteryAmpacity) ?? FUSE_SIZES.at(-1)!;
  const batteryCapacityOk = requiredBatteryAmpacity <= batteryMaxContinuousDischarge * batteryParallelCount;
  const batteryVoltageOk = Math.abs(batteryVoltage * batterySeriesCount - systemVoltage) <= 1;
  const inverterVoltageOk = Math.abs(input.inverterNominalVoltage - systemVoltage) <= 0.5;
  const inverterPeakOk = input.inverterPeakWatts >= maxLoadWatts;
  const loopLength = input.cableLength * 2;
  const allowedVoltageDrop = systemVoltage * Math.max(0.001, input.maxVoltageDrop);
  const exactCableArea = allowedVoltageDrop > 0
    ? (COPPER_RESISTIVITY * loopLength * maxCurrent) / allowedVoltageDrop
    : 0;
  const cableArea = STANDARD_CABLE_SIZES.find(size => size >= exactCableArea) ?? STANDARD_CABLE_SIZES.at(-1)!;
  const voltageDrop = maxCurrent > 0
    ? ((COPPER_RESISTIVITY * loopLength * maxCurrent) / (cableArea * systemVoltage)) * 100
    : 0;

  const systemLevels = {
    minimum: { batteryAh, panelWatts },
    balanced: { batteryAh: batteryAh * 1.25, panelWatts: panelWatts * 1.25 },
    expandable: { batteryAh: batteryAh * 1.5, panelWatts: panelWatts * 1.5 },
  };

  return {
    dailyWh,
    dailyDcWh,
    dailyAcWh,
    batteryAh,
    panelWatts,
    solarRequiredWh,
    dcDcChargingWh,
    shoreChargingWh,
    totalExternalChargingWh,
    dcDcAlternatorOk,
    maxLoadWatts,
    maxCurrent,
    inverterWatts,
    mpptCurrent,
    mpptAmps,
    mpptFuseAmps,
    arrayWatts,
    arrayVoc,
    arrayIsc,
    coldArrayVoc,
    seriesCount,
    parallelCount,
    mpptVoltageOk,
    mpptCurrentOk,
    mpptChargeCurrentOk,
    batteryCurrent,
    requiredBatteryAmpacity,
    recommendedFuseAmps,
    batteryCapacityOk,
    batteryVoltageOk,
    inverterVoltageOk,
    inverterPeakOk,
    systemLevels,
    voltageDrop,
    cableArea,
  };
}

export function getSolarSystemWarnings(result: SolarCalculationResult, input: SolarCalculationInput): string[] {
  const warnings: string[] = [];
  if (input.loads.length === 0 || result.dailyWh <= 0) warnings.push("Add at least one device with a positive runtime.");
  if (input.systemVoltage !== 12 && input.systemVoltage !== 24 && input.systemVoltage !== 48) warnings.push("Use a 12V, 24V or 48V system voltage.");
  if (input.usableDepthOfDischarge <= 0 || input.usableDepthOfDischarge > 1) warnings.push("Usable battery discharge must be between 1% and 100%.");
  if (input.sunHours <= 0) warnings.push("Peak sun hours must be greater than zero.");
  if (input.panelCount <= 0 || input.panelWatts <= 0 || input.panelVoc <= 0 || input.panelIsc <= 0) warnings.push("Enter positive panel quantity, wattage, Voc and Isc values before relying on PV compatibility results.");
  const batteryVoltage = Math.max(0.1, input.batteryNominalVoltage || input.systemVoltage);
  const batterySeriesCount = Math.max(1, Math.ceil(Math.max(0.1, input.systemVoltage) / batteryVoltage));
  const batteryParallelCount = Math.floor(Math.max(0, input.batteryCount) / batterySeriesCount);
  if (batterySeriesCount > 1 && batteryParallelCount < 1) warnings.push("The entered battery count cannot form one complete series string for this system voltage.");
  if (!result.batteryVoltageOk) warnings.push("The selected battery nominal voltage does not match the system voltage.");
  if (!result.inverterVoltageOk) warnings.push("The selected inverter nominal voltage does not match the system voltage.");
  if (!result.inverterPeakOk) warnings.push("The selected inverter peak rating is below the estimated simultaneous load.");
  if (!result.batteryCapacityOk) warnings.push("Estimated battery-side current exceeds the selected battery bank discharge limit.");
  if (!result.mpptVoltageOk) warnings.push("Cold-weather panel Voc exceeds the selected MPPT PV voltage limit.");
  if (!result.mpptCurrentOk) warnings.push("Panel-array Isc exceeds the selected MPPT PV short-circuit limit.");
  if (!result.mpptChargeCurrentOk) warnings.push("The required solar charge current is higher than the selected MPPT rating.");
  if (!result.dcDcAlternatorOk) warnings.push("DC-DC charger output exceeds the entered alternator spare-current limit.");
  return warnings;
}
