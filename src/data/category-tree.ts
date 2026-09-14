export type ContentScope = "caravan" | "marine" | "tiny-house" | "shared";

export type CategoryGroup = {
  name: string;
  slug: string;
  children: string[];
};

export type ContentScopeDefinition = {
  id: ContentScope;
  name: string;
  slug: string;
  groups: CategoryGroup[];
};

export const contentScopes: ContentScopeDefinition[] = [
  {
    id: "caravan",
    name: "Caravan Systems",
    slug: "caravan-systems",
    groups: [
      { name: "Power & Solar", slug: "power-solar", children: ["Solar & Energy", "Batteries & Charging"] },
      { name: "Water & Plumbing", slug: "water-plumbing", children: ["Freshwater & Wastewater"] },
      { name: "HVAC & Heating", slug: "hvac-heating", children: ["Climate Control", "Heating & Ventilation"] },
      { name: "Electrical & Wiring", slug: "electrical-wiring", children: ["DC Wiring", "AC Shore Power"] },
      { name: "Smart RV & IoT", slug: "smart-rv-iot", children: ["Automation & Monitoring"] },
      { name: "Towing & Weight", slug: "towing-weight", children: ["Payload & Stability", "Towing Safety"] },
    ],
  },
  {
    id: "marine",
    name: "Marine & Boat Systems",
    slug: "marine-boat-systems",
    groups: [
      { name: "Marine Power & Solar", slug: "marine-power-solar", children: ["Solar & Energy", "Batteries & Charging"] },
      { name: "Freshwater & Bilge", slug: "freshwater-bilge", children: ["Water Systems", "Bilge & Pumps"] },
      { name: "Marine HVAC", slug: "marine-hvac", children: ["Climate Control", "Ventilation"] },
      { name: "Wiring & Corrosion Protection", slug: "marine-wiring", children: ["DC Wiring", "Bonding & Corrosion"] },
      { name: "Navigation & IoT", slug: "navigation-iot", children: ["Monitoring & Telemetry"] },
      { name: "Weight & Stability", slug: "marine-stability", children: ["Load Distribution", "Stability & Trim"] },
    ],
  },
  {
    id: "tiny-house",
    name: "Tiny House Systems",
    slug: "tiny-house-systems",
    groups: [
      { name: "Off-Grid Power", slug: "tiny-house-power", children: ["Solar & Energy", "Batteries & Inverters"] },
      { name: "Water & Wastewater", slug: "tiny-house-water", children: ["Freshwater", "Wastewater & Treatment"] },
      { name: "Heating & Cooling", slug: "tiny-house-climate", children: ["Heating", "Cooling & Ventilation"] },
      { name: "Electrical Installation", slug: "tiny-house-electrical", children: ["AC Distribution", "DC Systems"] },
      { name: "Automation & Monitoring", slug: "tiny-house-automation", children: ["Energy Monitoring", "Smart Home Controls"] },
      { name: "Structure & Weight", slug: "tiny-house-structure", children: ["Load Planning", "Transport & Placement"] },
    ],
  },
  {
    id: "shared",
    name: "Shared Systems",
    slug: "shared-systems",
    groups: [
      { name: "Solar & Energy", slug: "shared-solar-energy", children: ["Energy Budgets", "Solar Sizing"] },
      { name: "Battery Storage", slug: "shared-battery-storage", children: ["Battery Sizing", "BMS & Protection"] },
      { name: "Water Systems", slug: "shared-water", children: ["Tank Sizing", "Pumps & Filtration"] },
      { name: "HVAC & Climate", slug: "shared-hvac", children: ["Heating", "Cooling & Ventilation"] },
      { name: "Electrical Engineering", slug: "shared-electrical", children: ["Cable Sizing", "Protection & Safety"] },
      { name: "Automation & IoT", slug: "shared-automation", children: ["Sensors", "Telemetry & Control"] },
    ],
  },
];

export const getScopeBySlug = (slug: string) => contentScopes.find(scope => scope.slug === slug);
