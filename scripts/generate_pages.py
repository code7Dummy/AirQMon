"""
Generate JSON data files consumed by the Astro static site.

Reads validated parquet data and produces:
  - src/data/current.json  -- current conditions for all stations
  - src/data/stations.json  -- station metadata index
  - src/data/counties.json  -- county index
  - public/sitemap.xml      -- sitemap for SEO

Usage:
    python scripts/generate_pages.py
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import polars as pl

DATA_DIR = Path(__file__).resolve().parent.parent / "src" / "data"
PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"

VALID_POLLUTANTS = ["PM10", "PM2.5", "NO2", "O3", "SO2", "CO", "C6H6", "BaP"]

# EEA 2024 AQI thresholds per pollutant
AQI_BANDS: dict[str, list[tuple[float, float, int, str, str]]] = {
    "PM2.5": [
        (0, 10, 1, "Good", "#50f0e6"),
        (10, 20, 2, "Fair", "#50ccaa"),
        (20, 25, 3, "Moderate", "#f0e641"),
        (25, 50, 4, "Poor", "#ff5050"),
        (50, 75, 5, "Very Poor", "#960032"),
        (75, float("inf"), 6, "Extremely Poor", "#7d2181"),
    ],
    "PM10": [
        (0, 20, 1, "Good", "#50f0e6"),
        (20, 40, 2, "Fair", "#50ccaa"),
        (40, 50, 3, "Moderate", "#f0e641"),
        (50, 100, 4, "Poor", "#ff5050"),
        (100, 150, 5, "Very Poor", "#960032"),
        (150, float("inf"), 6, "Extremely Poor", "#7d2181"),
    ],
    "NO2": [
        (0, 40, 1, "Good", "#50f0e6"),
        (40, 90, 2, "Fair", "#50ccaa"),
        (90, 120, 3, "Moderate", "#f0e641"),
        (120, 230, 4, "Poor", "#ff5050"),
        (230, 340, 5, "Very Poor", "#960032"),
        (340, float("inf"), 6, "Extremely Poor", "#7d2181"),
    ],
    "O3": [
        (0, 50, 1, "Good", "#50f0e6"),
        (50, 100, 2, "Fair", "#50ccaa"),
        (100, 130, 3, "Moderate", "#f0e641"),
        (130, 240, 4, "Poor", "#ff5050"),
        (240, 380, 5, "Very Poor", "#960032"),
        (380, float("inf"), 6, "Extremely Poor", "#7d2181"),
    ],
    "SO2": [
        (0, 100, 1, "Good", "#50f0e6"),
        (100, 200, 2, "Fair", "#50ccaa"),
        (200, 350, 3, "Moderate", "#f0e641"),
        (350, 500, 4, "Poor", "#ff5050"),
        (500, 750, 5, "Very Poor", "#960032"),
        (750, float("inf"), 6, "Extremely Poor", "#7d2181"),
    ],
    "CO": [
        (0, 5, 1, "Good", "#50f0e6"),
        (5, 10, 2, "Fair", "#50ccaa"),
        (10, 15, 3, "Moderate", "#f0e641"),
        (15, 25, 4, "Poor", "#ff5050"),
        (25, 35, 5, "Very Poor", "#960032"),
        (35, float("inf"), 6, "Extremely Poor", "#7d2181"),
    ],
    "C6H6": [
        (0, 5, 1, "Good", "#50f0e6"),
        (5, 10, 2, "Fair", "#50ccaa"),
        (10, 15, 3, "Moderate", "#f0e641"),
        (15, 25, 4, "Poor", "#ff5050"),
        (25, 35, 5, "Very Poor", "#960032"),
        (35, float("inf"), 6, "Extremely Poor", "#7d2181"),
    ],
    "BaP": [
        (0, 0.5, 1, "Good", "#50f0e6"),
        (0.5, 1, 2, "Fair", "#50ccaa"),
        (1, 1.5, 3, "Moderate", "#f0e641"),
        (1.5, 2.5, 4, "Poor", "#ff5050"),
        (2.5, 3.5, 5, "Very Poor", "#960032"),
        (3.5, float("inf"), 6, "Extremely Poor", "#7d2181"),
    ],
}

STATION_TYPE_EXPLANATIONS = {
    "background": "General area monitor — measures baseline air quality not dominated by a single nearby source.",
    "traffic": "Roadside monitor — placed near major roads to measure transport-related pollution exposure.",
    "industrial": "Industrial area monitor — located near industrial facilities to track emissions.",
    "unknown": "Station type not specified.",
}


def get_aqi(pollutant: str, value: float) -> tuple[int, str, str]:
    """Calculate AQI for a given pollutant and concentration."""
    bands = AQI_BANDS.get(pollutant)
    if not bands:
        return (1, "Good", "#50f0e6")

    for lo, hi, idx, label, color in bands:
        if lo <= value < hi:
            return (idx, label, color)
    # If value exceeds all thresholds, return highest band
    last = bands[-1]
    if last and value >= last[0]:
        return (last[2], last[3], last[4])
    return (1, "Good", "#50f0e6")


def get_overall_aqi(
    measurements: list[dict[str, Any]],
) -> tuple[int, str, str, str]:
    """Determine overall AQI as the worst (highest index) pollutant."""
    worst: tuple[int, str, str, str] = (1, "Good", "#50f0e6", "PM2.5")
    for m in measurements:
        idx, label, color = get_aqi(m["Pollutant"], m["Value"])
        if idx > worst[0]:
            worst = (idx, label, color, m["Pollutant"])
    return worst


def make_serializable(obj: Any) -> Any:
    """Convert Polars/numpy types to native Python types."""
    if isinstance(obj, pl.Series):
        return obj.to_list()
    if hasattr(obj, "item"):
        return obj.item()
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [make_serializable(x) for x in obj]
    return obj


def generate_current_json(df: pl.DataFrame, stations_df: pl.DataFrame) -> dict:
    """Build the current.json data structure for the dashboard."""
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    station_list: list[dict[str, Any]] = []

    # Group by station
    for row in stations_df.iter_rows(named=True):
        eoicode = row.get("AirQualityStationEoICode")
        if not eoicode:
            continue

        station_measurements = df.filter(
            pl.col("AirQualityStationEoICode") == eoicode
        )

        measurements: list[dict[str, Any]] = []
        for m_row in station_measurements.iter_rows(named=True):
            poll = m_row.get("Pollutant")
            val = m_row.get("Value")
            if poll is None or val is None or poll not in VALID_POLLUTANTS:
                continue
            measurements.append({
                "Samplingpoint": m_row.get("Samplingpoint", ""),
                "Pollutant": poll,
                "Start": str(m_row.get("Start", "")),
                "End": str(m_row.get("End", "")),
                "Value": float(val),
                "Unit": str(m_row.get("Unit", "µg/m³")),
                "AggType": str(m_row.get("AggType", "hour")),
                "Validity": int(m_row.get("Validity", 1)),
                "Verification": int(m_row.get("Verification", 3)),
                "ResultTime": str(m_row.get("ResultTime", now_utc)),
                "DataCapture": float(m_row["DataCapture"]) if m_row.get("DataCapture") is not None else None,
                "AirQualityStationEoICode": eoicode,
            })

        if not measurements:
            continue

        aqi_idx, aqi_label, aqi_color, dominant = get_overall_aqi(measurements)

        station_type = str(row.get("StationType", "background")).lower()
        station_area = str(row.get("StationArea", "urban")).lower()

        station_entry = {
            "station": {
                "AirQualityStationEoICode": eoicode,
                "Countrycode": str(row.get("Countrycode", "IE")),
                "StationType": station_type,
                "StationArea": station_area,
                "Longitude": float(row.get("Longitude", 0)),
                "Latitude": float(row.get("Latitude", 0)),
                "Altitude": float(row["Altitude"]) if row.get("Altitude") is not None else None,
                "NUTS1": str(row.get("NUTS1", "")) or None,
                "NUTS2": str(row.get("NUTS2", "")) or None,
                "NUTS3": str(row.get("NUTS3", "")) or None,
                "LAU_NAME": str(row.get("LAU_NAME", "")) or None,
                "CITY_NAME": str(row.get("CITY_NAME", "")) or None,
                "StationName": str(row.get("StationName", f"Station {eoicode}")),
                "DataCapture": float(row["DataCapture"]) if row.get("DataCapture") is not None else None,
                "StationTypeExplanation": STATION_TYPE_EXPLANATIONS.get(
                    station_type, STATION_TYPE_EXPLANATIONS["unknown"]
                ),
            },
            "measurements": measurements,
            "aqi": aqi_idx,
            "aqiLabel": aqi_label,
            "aqiColor": aqi_color,
            "dominantPollutant": dominant,
            "lastUpdated": now_utc,
        }
        station_list.append(station_entry)

    result = {
        "stations": station_list,
        "lastUpdated": now_utc,
        "buildTimestamp": now_utc,
    }
    return result


def generate_sitemap(stations: list[dict]) -> str:
    """Generate sitemap.xml."""
    base_url = "https://airquality.epa.ie"
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f"  <url><loc>{base_url}/</loc><priority>1.0</priority></url>",
        f"  <url><loc>{base_url}/methodology/</loc><priority>0.8</priority></url>",
        f"  <url><loc>{base_url}/about/</loc><priority>0.5</priority></url>",
    ]
    for s in stations:
        code = s.get("station", {}).get("AirQualityStationEoICode", "")
        if code:
            lines.append(
                f'  <url><loc>{base_url}/station/{code}/</loc><priority>0.7</priority></url>'
            )
    lines.append("</urlset>")
    return "\n".join(lines)


def main():
    validated_path = DATA_DIR / "validated.parquet"
    stations_path = DATA_DIR / "stations.parquet"

    if not validated_path.exists() or not stations_path.exists():
        print("No validated data found. Run scripts/validate.py first.")
        # Generate empty data files so the site can build
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        empty = {"stations": [], "lastUpdated": now, "buildTimestamp": now}

        current_out = DATA_DIR / "current.json"
        current_out.write_text(json.dumps(empty, indent=2))
        print(f"Wrote empty {current_out}")

        # Empty sitemap
        sitemap = PUBLIC_DIR / "sitemap.xml"
        sitemap.write_text(generate_sitemap([]))
        print(f"Wrote empty sitemap to {sitemap}")

        return

    print("Loading validated data...")
    df = pl.read_parquet(validated_path)
    stations_df = pl.read_parquet(stations_path)
    print(f"Loaded {df.height} measurements across {stations_df.height} stations")

    # Generate current.json
    current_data = generate_current_json(df, stations_df)
    current_out = DATA_DIR / "current.json"
    serialized = make_serializable(current_data)
    current_out.write_text(json.dumps(serialized, indent=2))
    print(f"Wrote {current_out} ({len(serialized['stations'])} stations)")

    # Generate sitemap.xml
    sitemap = PUBLIC_DIR / "sitemap.xml"
    sitemap.write_text(generate_sitemap(serialized["stations"]))
    print(f"Wrote sitemap to {sitemap}")

    print("Done.")


if __name__ == "__main__":
    main()
