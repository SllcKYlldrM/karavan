export type WaterCalculationInput = {
  tankCapacityLitres: number;
  people: number;
  drinkingLitresPerPerson: number;
  cookingLitresPerPerson: number;
  dishesLitresPerPerson: number;
  showerMinutesPerPerson: number;
  showerFlowLitresPerMinute: number;
  toiletUsesPerPerson: number;
  toiletLitresPerUse: number;
  otherLitresPerDay: number;
  reserveFactor: number;
  greyWaterTankCapacityLitres: number;
};

export type WaterCalculationResult = {
  dailyUseLitres: number;
  tankDays: number;
  requiredTankLitres: number;
  recommendedTankLitres: number;
  freshWaterWeightKg: number;
  greyWaterLitres: number;
  greyWaterCapacityOk: boolean;
};

export function calculateWater(input: WaterCalculationInput): WaterCalculationResult {
  const people = Math.max(1, input.people);
  const drinking = Math.max(0, input.drinkingLitresPerPerson);
  const cooking = Math.max(0, input.cookingLitresPerPerson);
  const dishes = Math.max(0, input.dishesLitresPerPerson);
  const showerMinutes = Math.max(0, input.showerMinutesPerPerson);
  const showerFlow = Math.max(0, input.showerFlowLitresPerMinute);
  const toiletUses = Math.max(0, input.toiletUsesPerPerson);
  const toiletLitres = Math.max(0, input.toiletLitresPerUse);
  const dailyPersonalUse = people * (
    drinking + cooking + dishes + showerMinutes * showerFlow + toiletUses * toiletLitres
  );
  const dailyUseLitres = Math.max(0, dailyPersonalUse + Math.max(0, input.otherLitresPerDay));
  const reserveFactor = Math.max(1, input.reserveFactor);
  const requiredTankLitres = dailyUseLitres * reserveFactor;
  const recommendedTankLitres = Math.ceil(requiredTankLitres / 5) * 5;
  const greyWaterLitres = Math.max(0, dailyUseLitres - people * drinking);

  return {
    dailyUseLitres,
    tankDays: dailyUseLitres > 0 ? Math.max(0, input.tankCapacityLitres) / dailyUseLitres : 0,
    requiredTankLitres,
    recommendedTankLitres,
    freshWaterWeightKg: Math.max(0, input.tankCapacityLitres),
    greyWaterLitres,
    greyWaterCapacityOk: input.greyWaterTankCapacityLitres <= 0 || input.greyWaterTankCapacityLitres >= greyWaterLitres,
  };
}
