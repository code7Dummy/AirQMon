export const SITE_TITLE = "Air Quality Ireland — Live AQI, PM2.5, PM10, Pollution Levels";
export const SITE_DESCRIPTION =
  "Real-time air quality data for Ireland. Live AQI, PM2.5, PM10, NO2, O3 and pollution levels from official monitoring stations. Updated hourly.";
export const SITE_KEYWORDS =
  "air quality ireland, aqi ireland, pm2.5 ireland, pollution dublin, air quality monitor, real time air quality, irish air pollution, live aqi, pm10 ireland, no2 levels, ozone monitoring";

export const EEA_API_BASE = "https://eeadmz1-downloads-api-appservice.azurewebsites.net";
export const EPA_STATION_REGISTRY =
  "https://www.epa.ie/";
export const ZENODO_BOOTSTRAP = "https://zenodo.org/records/14513586";

export const COUNTRY_CODE = "IE";
export const PRIMARY_POLLUTANTS = ["PM10", "PM2.5", "NO2", "O3", "SO2"] as const;

export const DISCLAIMER_DATA =
  "Air quality data from the European Environment Agency (EEA) Air Quality e-Reporting system and the Environmental Protection Agency (EPA) Ireland. Real-time data is unverified and subject to revision.";

export const DISCLAIMER_MEDICAL =
  "This site is for informational purposes only and does not provide medical or legal advice. For health concerns, consult a medical professional.";

export const DISCLAIMER_PRELIMINARY =
  "Showing preliminary unverified data from the EEA E2a dataset. Data may be revised when verified (E1a) data becomes available.";

export const IRELAND_BOUNDS = {
  north: 55.43,
  south: 51.39,
  east: -5.45,
  west: -10.67,
};

export const MAP_DEFAULT_CENTER: [number, number] = [53.35, -7.5];
export const MAP_DEFAULT_ZOOM = 7;

export const BUY_ME_A_COFFEE_URL = "https://www.buymeacoffee.com/";
export const REFRESH_INTERVAL_HOURS = 6;
export const DATA_SOURCES = [
  { name: "EEA Air Quality e-Reporting (E2a)", type: "Real-time unverified" },
  { name: "EEA Air Quality e-Reporting (E1a)", type: "Annual verified" },
  { name: "EPA Ireland Station Registry", type: "Station metadata" },
] as const;
