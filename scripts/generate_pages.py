import polars as pl
import json, os, sys
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

VALIDATED_DIR = Path(__file__).resolve().parent.parent / "data" / "validated"
DATA_DIR = Path(__file__).resolve().parent.parent / "src" / "data"
META_DIR = Path(__file__).resolve().parent.parent / "data"

AQI_DEFS = {
    "PM2.5": [(1, "#50f0e6", 0, 10), (2, "#50ccaa", 10, 20), (3, "#f0e641", 20, 25), (4, "#ff5050", 25, 50), (5, "#960032", 50, 75), (6, "#7d2181", 75, float("inf"))],
    "PM10":  [(1, "#50f0e6", 0, 20), (2, "#50ccaa", 20, 40), (3, "#f0e641", 40, 50), (4, "#ff5050", 50, 100), (5, "#960032", 100, 150), (6, "#7d2181", 150, float("inf"))],
    "NO2":   [(1, "#50f0e6", 0, 40), (2, "#50ccaa", 40, 90), (3, "#f0e641", 90, 120), (4, "#ff5050", 120, 230), (5, "#960032", 230, 340), (6, "#7d2181", 340, float("inf"))],
    "O3":    [(1, "#50f0e6", 0, 50), (2, "#50ccaa", 50, 100), (3, "#f0e641", 100, 130), (4, "#ff5050", 130, 240), (5, "#960032", 240, 380), (6, "#7d2181", 380, float("inf"))],
    "SO2":   [(1, "#50f0e6", 0, 100), (2, "#50ccaa", 100, 200), (3, "#f0e641", 200, 350), (4, "#ff5050", 350, 500), (5, "#960032", 500, 750), (6, "#7d2181", 750, float("inf"))],
}

AQI_LABELS = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor", 6: "Extremely Poor"}

def get_aqi(pollutant, value):
    bands = AQI_DEFS.get(pollutant)
    if not bands:
        return (1, "#50f0e6", "Good")
    for idx, color, lo, hi in bands:
        if lo <= value < hi:
            return (idx, color, AQI_LABELS[idx])
    last = bands[-1]
    return (last[0], last[1], AQI_LABELS[last[0]])

def get_overall_aqi(measurements):
    worst = None
    for m in measurements:
        idx, color, label = get_aqi(m["Pollutant"], m["Value"])
        if worst is None or idx > worst[0]:
            worst = (idx, color, label, m["Pollutant"])
    if worst is None:
        return (1, "#50f0e6", "Good", "PM2.5")
    return worst

def flatten_station_type(st):
    st = st.lower().replace(" ", "").replace("-", "").replace("_", "")
    if any(t in st for t in ("background", "rural", "regional", "cúlra")):
        return "background"
    if any(t in st for t in ("industrial", "industrialsource", "tionsclaíoch")):
        return "industrial"
    if any(t in st for t in ("traffic", "roadside", "road", "trácht")):
        return "traffic"
    return "background"

def flatten_station_area(st):
    st = st.lower().replace(" ", "").replace("-", "").replace("_", "")
    if "urban" in st or "uibeach" in st:
        return "urban"
    if "suburban" in st or "fo-uirbeach" in st:
        return "suburban"
    if "rural" in st or "tuaithe" in st:
        return "rural"
    return "urban"

def load_station_metadata():
    stations_json = META_DIR / "stations.json"
    if stations_json.exists():
        with open(stations_json, "r", encoding="utf-8") as f:
            meta = json.load(f)
        print(f"Loaded {len(meta)} station metadata records from {stations_json}")
        return meta
    print("No local station metadata found")
    return {}

def main():
    input_path = VALIDATED_DIR / "e2a_validated.parquet"
    if not input_path.exists():
        print("No validated data found. Run validate.py first.")
        sys.exit(1)

    df = pl.read_parquet(input_path)
    print(f"Read {df.height} rows")

    meta = load_station_metadata()

    # Group by station code
    station_groups = defaultdict(list)
    for row in df.to_dicts():
        code = row["AirQualityStationEoICode"]
        station_groups[code].append(row)

    stations_out = []
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for code in sorted(station_groups.keys()):
        rows = station_groups[code]
        rows.sort(key=lambda r: r["End"], reverse=True)

        seen_pollutants = {}
        for r in rows:
            p = r["PollutantName"]
            if p not in seen_pollutants:
                seen_pollutants[p] = r

        measurements = []
        for p, r in seen_pollutants.items():
            val = round(float(r["Value"]), 1) if r["Value"] is not None else None
            if val is None:
                continue
            measurements.append({
                "Samplingpoint": r["Samplingpoint"],
                "Pollutant": r["PollutantName"],
                "Start": str(r["Start"]) if r["Start"] else None,
                "End": str(r["End"]) if r["End"] else None,
                "Value": val,
                "Unit": r.get("Unit", "µg/m³") or "µg/m³",
                "AggType": r.get("AggType", ""),
                "Validity": r["Validity"],
                "Verification": r.get("Verification"),
                "ResultTime": str(r["ResultTime"]) if r.get("ResultTime") else now_iso,
                "DataCapture": float(r["DataCapture"]) if r.get("DataCapture") is not None else None,
                "AirQualityStationEoICode": code,
            })

        if not measurements:
            continue

        aqi_idx, aqi_color, aqi_label, dominant = get_overall_aqi(measurements)

        md = meta.get(code, {})
        st_type_raw = md.get("StationType", "background") if md else "background"
        st_area_raw = md.get("StationArea", "urban") if md else "urban"
        station_type = flatten_station_type(str(st_type_raw))
        station_area = flatten_station_area(str(st_area_raw))

        try:
            lat = float(md["Latitude"]) if md.get("Latitude") else None
        except (ValueError, TypeError):
            lat = None
        try:
            lng = float(md["Longitude"]) if md.get("Longitude") else None
        except (ValueError, TypeError):
            lng = None
        try:
            alt = float(md["Elevation"]) if md.get("Elevation") else None
        except (ValueError, TypeError):
            alt = None

        station_name = md.get("StationName", code) if md else code
        city_name = md.get("CITY_NAME", md.get("CityName", "")) if md else ""

        station_entry = {
            "station": {
                "AirQualityStationEoICode": code,
                "Countrycode": "IE",
                "StationType": station_type,
                "StationArea": station_area,
                "Longitude": lng,
                "Latitude": lat,
                "Altitude": alt,
                "NUTS1": md.get("NUTS1", "") if md else "",
                "NUTS2": md.get("NUTS2", "") if md else "",
                "NUTS3": md.get("NUTS3", "") if md else "",
                "LAU_NAME": md.get("LAU_NAME", "") if md else "",
                "CITY_NAME": city_name,
                "StationName": station_name,
                "DataCapture": None,
                "StationTypeExplanation": {
                    "background": "General area monitor — measures baseline air quality not dominated by a single nearby source.",
                    "industrial": "Industrial area monitor — located near industrial facilities to track emissions.",
                    "traffic": "Roadside monitor — placed near major roads to measure transport-related pollution exposure.",
                }.get(station_type, "Air quality monitoring station."),
            },
            "measurements": measurements,
            "aqi": aqi_idx,
            "aqiLabel": aqi_label,
            "aqiColor": aqi_color,
            "dominantPollutant": dominant,
            "lastUpdated": max((m["ResultTime"] for m in measurements if m["ResultTime"]), default=now_iso),
        }
        stations_out.append(station_entry)

    output = {
        "stations": stations_out,
        "lastUpdated": now_iso,
        "buildTimestamp": now_iso,
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DATA_DIR / "current.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    named = [(s["station"]["StationName"], s["station"]["AirQualityStationEoICode"], s["station"]["Latitude"]) for s in stations_out]
    with_coords = sum(1 for _, _, lat in named if lat is not None)
    print(f"\nWrote {output_path} with {len(stations_out)} stations ({with_coords} with coordinates)")
    for name, code, lat in named:
        coord = f" ({lat}, …)" if lat else ""
        print(f"  {name} ({code}){coord}")

if __name__ == "__main__":
    main()
