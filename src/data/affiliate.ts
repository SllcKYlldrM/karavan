export type AffiliateOffer = {
  id: string;
  title: string;
  category: "solar" | "battery" | "inverter" | "cable" | "fuse" | "water" | "heating" | "towing";
  description: string;
  merchant: string;
  url: string;
  sourceUrl: string;
  lastChecked: string;
  disclosureRequired: boolean;
};

/** Keep monetization disabled until a program is approved and offers are reviewed. */
export const affiliateEnabled = false;

/** Product offers are intentionally empty until they have a verified source and destination URL. */
export const affiliateOffers: AffiliateOffer[] = [];

export const affiliateDisclosure =
  "Some product links may be affiliate links. If you buy through one, VanSpecs may earn a commission at no extra cost to you.";
