export const VALIDITY_LABELS: Record<number, string> = {
  1: "Confirmed reading",
  2: "Trace amount (below sensor threshold)",
  3: "Estimated trace amount",
  [-1]: "Reading unavailable",
  [-99]: "Station maintenance",
};

export const VERIFICATION_LABELS: Record<number, string> = {
  1: "Official verified data",
  2: "Preliminary check passed",
  3: "Real-time, not yet verified",
};

export const STATION_TYPE_LABELS: Record<string, string> = {
  background: "General area monitor",
  industrial: "Industrial area monitor",
  traffic: "Roadside monitor",
};

export const STATION_AREA_LABELS: Record<string, string> = {
  urban: "Urban area",
  suburban: "Suburban area",
  rural: "Rural area",
  "rural-nearcity": "Rural area near city",
  "rural-regional": "Regional rural area",
  "rural-remote": "Remote rural area",
};

export const POLLUTANT_NAMES: Record<string, string> = {
  PM10: "Particulate Matter ≤10µm (PM₁₀)",
  "PM2.5": "Fine Particulate Matter ≤2.5µm (PM₂.₅)",
  NO2: "Nitrogen Dioxide (NO₂)",
  O3: "Ozone (O₃)",
  SO2: "Sulphur Dioxide (SO₂)",
  CO: "Carbon Monoxide (CO)",
  C6H6: "Benzene (C₆H₆)",
  BaP: "Benzo[a]pyrene (BaP)",
};

export const POLLUTANT_HEALTH_INFO: Record<string, string> = {
  PM10: "Inhalable particles that can penetrate the lungs. Sources include road dust, construction, and industrial processes.",
  "PM2.5": "Fine particles that can enter the bloodstream. Associated with respiratory and cardiovascular issues. Major sources: combustion engines, heating, industry.",
  NO2: "Irritant gas affecting respiratory system. Primarily from traffic emissions and combustion processes.",
  O3: "Ground-level ozone formed by reactions of pollutants in sunlight. Can irritate airways and worsen lung conditions.",
  SO2: "Gas produced by burning fossil fuels. Can cause respiratory irritation, particularly for asthma patients.",
  CO: "Odorless gas from incomplete combustion. Reduces blood oxygen capacity. Sources: traffic, heating.",
  C6H6: "Volatile organic compound from traffic and industrial sources. Known carcinogen with long-term exposure risks.",
  BaP: "Polycyclic aromatic hydrocarbon from combustion. Known carcinogen. Sources: traffic, heating, industry.",
};

export const AQI_HEALTH_ADVICE: Record<number, { general: string; sensitive: string }> = {
  1: {
    general: "Air quality is satisfactory. Enjoy normal outdoor activities.",
    sensitive: "No health implications. Enjoy normal activities.",
  },
  2: {
    general: "Air quality is acceptable. Enjoy normal outdoor activities.",
    sensitive: "Consider reducing prolonged outdoor exertion if experiencing symptoms.",
  },
  3: {
    general: "Sensitive individuals should consider reducing prolonged outdoor exertion.",
    sensitive: "Reduce prolonged outdoor exertion. Monitor symptoms.",
  },
  4: {
    general: "Reduce prolonged outdoor exertion. Consider rescheduling outdoor activities.",
    sensitive: "Avoid prolonged outdoor exertion. Consider indoor activities.",
  },
  5: {
    general: "Avoid prolonged outdoor exertion. Reschedule outdoor activities if possible.",
    sensitive: "Avoid all outdoor exertion. Keep windows closed.",
  },
  6: {
    general: "Avoid all outdoor physical activity. Stay indoors with windows closed.",
    sensitive: "Stay indoors with windows closed. Seek medical advice if symptoms occur.",
  },
};
