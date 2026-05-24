import type { Pollutant, AqiBand, PollutantAqiInfo, AqiIndex } from "./types";

const AQI_DEFINITIONS: Record<Pollutant, PollutantAqiInfo> = {
  "PM2.5": {
    euAnnualLimit: 5,
    whoGuideline: 5,
    unit: "µg/m³",
    bands: [
      { index: 1, label: "Good", color: "#50f0e6", range: [0, 10] },
      { index: 2, label: "Fair", color: "#50ccaa", range: [10, 20] },
      { index: 3, label: "Moderate", color: "#f0e641", range: [20, 25] },
      { index: 4, label: "Poor", color: "#ff5050", range: [25, 50] },
      { index: 5, label: "Very Poor", color: "#960032", range: [50, 75] },
      { index: 6, label: "Extremely Poor", color: "#7d2181", range: [75, Infinity] },
    ],
  },
  PM10: {
    euAnnualLimit: 20,
    whoGuideline: 15,
    unit: "µg/m³",
    bands: [
      { index: 1, label: "Good", color: "#50f0e6", range: [0, 20] },
      { index: 2, label: "Fair", color: "#50ccaa", range: [20, 40] },
      { index: 3, label: "Moderate", color: "#f0e641", range: [40, 50] },
      { index: 4, label: "Poor", color: "#ff5050", range: [50, 100] },
      { index: 5, label: "Very Poor", color: "#960032", range: [100, 150] },
      { index: 6, label: "Extremely Poor", color: "#7d2181", range: [150, Infinity] },
    ],
  },
  NO2: {
    euAnnualLimit: 10,
    whoGuideline: 10,
    unit: "µg/m³",
    bands: [
      { index: 1, label: "Good", color: "#50f0e6", range: [0, 40] },
      { index: 2, label: "Fair", color: "#50ccaa", range: [40, 90] },
      { index: 3, label: "Moderate", color: "#f0e641", range: [90, 120] },
      { index: 4, label: "Poor", color: "#ff5050", range: [120, 230] },
      { index: 5, label: "Very Poor", color: "#960032", range: [230, 340] },
      { index: 6, label: "Extremely Poor", color: "#7d2181", range: [340, Infinity] },
    ],
  },
  O3: {
    euAnnualLimit: 120,
    whoGuideline: 100,
    unit: "µg/m³",
    bands: [
      { index: 1, label: "Good", color: "#50f0e6", range: [0, 50] },
      { index: 2, label: "Fair", color: "#50ccaa", range: [50, 100] },
      { index: 3, label: "Moderate", color: "#f0e641", range: [100, 130] },
      { index: 4, label: "Poor", color: "#ff5050", range: [130, 240] },
      { index: 5, label: "Very Poor", color: "#960032", range: [240, 380] },
      { index: 6, label: "Extremely Poor", color: "#7d2181", range: [380, Infinity] },
    ],
  },
  SO2: {
    euAnnualLimit: 20,
    whoGuideline: 40,
    unit: "µg/m³",
    bands: [
      { index: 1, label: "Good", color: "#50f0e6", range: [0, 100] },
      { index: 2, label: "Fair", color: "#50ccaa", range: [100, 200] },
      { index: 3, label: "Moderate", color: "#f0e641", range: [200, 350] },
      { index: 4, label: "Poor", color: "#ff5050", range: [350, 500] },
      { index: 5, label: "Very Poor", color: "#960032", range: [500, 750] },
      { index: 6, label: "Extremely Poor", color: "#7d2181", range: [750, Infinity] },
    ],
  },
  CO: {
    euAnnualLimit: 5,
    whoGuideline: 4,
    unit: "mg/m³",
    bands: [
      { index: 1, label: "Good", color: "#50f0e6", range: [0, 5] },
      { index: 2, label: "Fair", color: "#50ccaa", range: [5, 10] },
      { index: 3, label: "Moderate", color: "#f0e641", range: [10, 15] },
      { index: 4, label: "Poor", color: "#ff5050", range: [15, 25] },
      { index: 5, label: "Very Poor", color: "#960032", range: [25, 35] },
      { index: 6, label: "Extremely Poor", color: "#7d2181", range: [35, Infinity] },
    ],
  },
  C6H6: {
    euAnnualLimit: 1,
    whoGuideline: 1,
    unit: "µg/m³",
    bands: [
      { index: 1, label: "Good", color: "#50f0e6", range: [0, 5] },
      { index: 2, label: "Fair", color: "#50ccaa", range: [5, 10] },
      { index: 3, label: "Moderate", color: "#f0e641", range: [10, 15] },
      { index: 4, label: "Poor", color: "#ff5050", range: [15, 25] },
      { index: 5, label: "Very Poor", color: "#960032", range: [25, 35] },
      { index: 6, label: "Extremely Poor", color: "#7d2181", range: [35, Infinity] },
    ],
  },
  BaP: {
    euAnnualLimit: 0.5,
    whoGuideline: 0.5,
    unit: "ng/m³",
    bands: [
      { index: 1, label: "Good", color: "#50f0e6", range: [0, 0.5] },
      { index: 2, label: "Fair", color: "#50ccaa", range: [0.5, 1] },
      { index: 3, label: "Moderate", color: "#f0e641", range: [1, 1.5] },
      { index: 4, label: "Poor", color: "#ff5050", range: [1.5, 2.5] },
      { index: 5, label: "Very Poor", color: "#960032", range: [2.5, 3.5] },
      { index: 6, label: "Extremely Poor", color: "#7d2181", range: [3.5, Infinity] },
    ],
  },
};

export function getAqiForPollutant(
  pollutant: Pollutant,
  value: number,
): { index: AqiIndex; label: string; color: string } {
  const info = AQI_DEFINITIONS[pollutant];
  if (!info) return { index: 1, label: "Good", color: "#50f0e6" };

  for (const band of info.bands) {
    if (value >= band.range[0] && value < band.range[1]) {
      return { index: band.index as AqiIndex, label: band.label, color: band.color };
    }
  }

  const lastBand = info.bands[info.bands.length - 1];
  if (lastBand && value >= lastBand.range[0]) {
    return { index: lastBand.index as AqiIndex, label: lastBand.label, color: lastBand.color };
  }

  return { index: 1, label: "Good", color: "#50f0e6" };
}

export function getOverallAqi(
  measurements: { pollutant: Pollutant; value: number }[],
): { index: AqiIndex; label: string; color: string; dominantPollutant: Pollutant } {
  let worst: { index: AqiIndex; label: string; color: string; pollutant: Pollutant } | null = null;

  for (const m of measurements) {
    const aqi = getAqiForPollutant(m.pollutant, m.value);
    if (!worst || aqi.index > worst.index) {
      worst = { ...aqi, pollutant: m.pollutant };
    }
  }

  if (!worst) {
    return { index: 1, label: "Good", color: "#50f0e6", dominantPollutant: "PM2.5" };
  }

  return {
    index: worst.index,
    label: worst.label,
    color: worst.color,
    dominantPollutant: worst.pollutant,
  };
}

export function getPollutantInfo(pollutant: Pollutant): PollutantAqiInfo | undefined {
  return AQI_DEFINITIONS[pollutant];
}

export function isWithinEULimit(pollutant: Pollutant, value: number): boolean {
  const info = AQI_DEFINITIONS[pollutant];
  if (!info) return true;
  return value <= info.euAnnualLimit;
}

export { AQI_DEFINITIONS };
