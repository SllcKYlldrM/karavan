export type AppliancePreset = {
  id: string;
  name: string;
  watts: number;
  defaultHours: number;
  isAc?: boolean;
};

export const appliancePresets: AppliancePreset[] = [
  { id: "fridge", name: "Compressor refrigerator", watts: 60, defaultHours: 8, isAc: true },
  { id: "lighting", name: "LED lighting", watts: 40, defaultHours: 5 },
  { id: "water-pump", name: "Water pump", watts: 60, defaultHours: 0.5 },
  { id: "laptop", name: "Laptop / electronics", watts: 65, defaultHours: 3, isAc: true },
  { id: "tv", name: "Television", watts: 80, defaultHours: 2, isAc: true },
  { id: "custom", name: "Custom device", watts: 100, defaultHours: 1 },
];
