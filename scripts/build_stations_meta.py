import requests, json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

# Fetch EPA station data via WFS
url = "https://gis.epa.ie/geoserver/EPA/ows"
params = {
    "service": "WFS",
    "version": "1.0.0",
    "request": "GetFeature",
    "typeName": "EPA:AIR_MonitoringSites",
    "maxFeatures": 200,
    "outputFormat": "application/json",
    "srsName": "EPSG:4326",
}
r = requests.get(url, params=params, timeout=30)
features = r.json()["features"]

# Build lookup by Eionet_Code and Station_Code
epa_by_eionet = {}
epa_by_station = {}
for f in features:
    p = f["properties"]
    coords = f["geometry"]["coordinates"]
    lat = coords[0][1] if coords and coords[0] else None
    lng = coords[0][0] if coords and coords[0] else None

    station_type = str(p.get("Station_Classification", "") or "").lower()
    station_area = str(p.get("Area_Classification", "") or "").lower()

    entry = {
        "StationName": p.get("Station_Name", ""),
        "StationCode": p.get("Station_Code", ""),
        "EionetCode": p.get("Eionet_Code"),
        "Latitude": lat,
        "Longitude": lng,
        "StationType": station_type if station_type else "background",
        "StationArea": station_area if station_area else "urban",
        "MonitoringType": p.get("Monitoring_Type", ""),
        "Parameters": [str(p.get(f"Parameter_{i}", "")) for i in range(1, 6) if p.get(f"Parameter_{i}")],
    }
    eionet = p.get("Eionet_Code")
    if eionet and eionet not in ("None", "N/A", ""):
        epa_by_eionet[eionet] = entry
    st_code = p.get("Station_Code")
    if st_code and st_code not in ("None", "N/A", ""):
        epa_by_station[st_code] = entry

# Also index by Name for backup lookup
epa_by_name = {}
for f in features:
    p = f["properties"]
    name = (p.get("Station_Name", "") or "").strip().lower()
    if name:
        epa_by_name[name] = p

# Read station codes from EEA data
import polars as pl
df = pl.read_parquet(str(PROJECT / "data" / "validated" / "e2a_validated.parquet"))
codes = sorted(df["AirQualityStationEoICode"].unique().to_list())

print(f"EEA station codes: {len(codes)}")
print(f"EPA by Eionet: {len(epa_by_eionet)}")
print(f"EPA by Station Code: {len(epa_by_station)}")

# Build metadata
meta = {}
matched_by_eionet = 0
matched_by_code = 0
matched_by_name = 0
unmatched = []

for code in codes:
    entry = epa_by_eionet.get(code)
    if entry:
        matched_by_eionet += 1
    else:
        entry = epa_by_station.get(code)
        if entry:
            matched_by_code += 1
        else:
            # Try matching by checking if code is contained in station code
            for st_code, st_entry in epa_by_station.items():
                if code.lower() == st_code.lower():
                    entry = st_entry
                    matched_by_code += 1
                    break

    if entry:
        meta[code] = {
            "StationName": entry["StationName"] or code,
            "Latitude": entry["Latitude"],
            "Longitude": entry["Longitude"],
            "StationType": entry["StationType"],
            "StationArea": entry["StationArea"],
            "Elevation": None,
            "CITY_NAME": (entry["StationName"] or "").split("(")[0].strip(),
        }
    else:
        unmatched.append(code)
        meta[code] = {
            "StationName": code,
            "Latitude": None,
            "Longitude": None,
            "StationType": "background",
            "StationArea": "urban",
            "Elevation": None,
            "CITY_NAME": "",
        }

print(f"\nMatched by Eionet code: {matched_by_eionet}")
print(f"Matched by station code: {matched_by_code}")
print(f"Unmatched: {len(unmatched)}")
if unmatched:
    print(f"Unmatched codes: {unmatched}")

# Save
output_path = PROJECT / "data" / "stations.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(meta, f, indent=2, ensure_ascii=False)
print(f"\nSaved {len(meta)} stations to {output_path}")

# Verify
matched = [c for c in codes if c in meta]
print(f"Total stations with coordinates: {sum(1 for c in codes if meta[c]['Latitude'] is not None)}")
