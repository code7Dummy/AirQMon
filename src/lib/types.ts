export type Pollutant = "PM10" | "PM2.5" | "NO2" | "O3" | "SO2" | "CO" | "C6H6" | "BaP";

export type StationType = "background" | "industrial" | "traffic";

export type StationArea =
  | "urban"
  | "suburban"
  | "rural"
  | "rural-nearcity"
  | "rural-regional"
  | "rural-remote";

export type AggType = "hour" | "day" | "var";

export type VerificationStatus = 1 | 2 | 3;

export interface Station {
  AirQualityStationEoICode: string;
  Countrycode: string;
  StationType: StationType;
  StationArea: StationArea;
  Longitude: number;
  Latitude: number;
  Altitude: number | null;
  NUTS1: string | null;
  NUTS2: string | null;
  NUTS3: string | null;
  LAU_NAME: string | null;
  CITY_NAME: string | null;
  StationName: string;
  DataCapture: number | null;
  StationTypeExplanation: string;
}

export interface Measurement {
  Samplingpoint: string;
  Pollutant: Pollutant;
  Start: string;
  End: string;
  Value: number;
  Unit: string;
  AggType: AggType;
  Validity: number;
  Verification: VerificationStatus;
  ResultTime: string;
  DataCapture: number | null;
  AirQualityStationEoICode: string;
}

export interface AqiBand {
  index: number;
  label: string;
  color: string;
  range: [number, number];
}

export interface PollutantAqiInfo {
  bands: AqiBand[];
  euAnnualLimit: number;
  unit: string;
  whoGuideline: number;
}

export interface StationCurrentData {
  station: Station;
  measurements: Measurement[];
  aqi: number;
  aqiLabel: string;
  aqiColor: string;
  dominantPollutant: Pollutant;
  lastUpdated: string;
}

export type AqiIndex = 1 | 2 | 3 | 4 | 5 | 6;

export interface SiteData {
  stations: StationCurrentData[];
  lastUpdated: string;
  buildTimestamp: string;
}
