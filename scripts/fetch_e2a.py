"""
Fetch E2a (up-to-date) air quality data from the EEA Download Service API.

Filters for Ireland (IE), key pollutants (PM10, PM2.5, NO2, O3, SO2),
and the last 48 hours of hourly data.

Usage:
    python scripts/fetch_e2a.py

Output:
    data/raw_e2a.parquet  -- raw parquet file with latest measurements
"""

import json
import os
import requests
from pathlib import Path

EEA_API_URL = os.environ.get(
    "EEA_API_URL",
    "https://eeadmz1-downloads-api-appservice.azurewebsites.net",
)
DATA_DIR = Path(__file__).resolve().parent.parent / "src" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def fetch_e2a_urls() -> list[str]:
    """Get signed Azure Blob URLs for E2a parquet files matching our filter."""
    payload = {
        "countries": ["IE"],
        "pollutants": ["PM10", "PM2.5", "NO2", "O3", "SO2", "CO", "C6H6", "BaP"],
        "dataset": 2,  # E2a up-to-date
        "aggregationType": "hour",
    }
    url = f"{EEA_API_URL}/ParquetFile/urls"
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    result = resp.json()
    # Response is typically a list of signed URLs or a dict with a 'urls' key
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        return result.get("urls", result.get("Urls", []))
    raise ValueError(f"Unexpected response format: {type(result)}")


def fetch_e2a_dynamic() -> bytes:
    """Fetch filtered data directly via the dynamic endpoint."""
    payload = {
        "countries": ["IE"],
        "pollutants": ["PM10", "PM2.5", "NO2", "O3", "SO2"],
        "dataset": 2,
        "aggregationType": "hour",
    }
    url = f"{EEA_API_URL}/ParquetFile/dynamic"
    resp = requests.post(url, json=payload, timeout=300)
    resp.raise_for_status()
    return resp.content


def main():
    print("Fetching E2a data for Ireland...")

    try:
        # Try the dynamic endpoint first (gives filtered data directly)
        raw_data = fetch_e2a_dynamic()
        output_path = DATA_DIR / "raw_e2a.parquet"
        output_path.write_bytes(raw_data)
        print(f"Saved dynamic E2a parquet ({len(raw_data) / 1024 / 1024:.1f} MB) to {output_path}")

    except Exception as e:
        print(f"Dynamic fetch failed ({e}), falling back to URL-based fetch...")
        try:
            urls = fetch_e2a_urls()
            if not urls:
                print("No URLs returned from API.")
                return

            combined = bytearray()
            for i, file_url in enumerate(urls):
                print(f"Downloading part {i + 1}/{len(urls)}...")
                resp = requests.get(file_url, timeout=300)
                resp.raise_for_status()
                combined.extend(resp.content)

            output_path = DATA_DIR / "raw_e2a.parquet"
            output_path.write_bytes(bytes(combined))
            print(f"Saved combined E2a parquet ({len(combined) / 1024 / 1024:.1f} MB) to {output_path}")

        except Exception as e2:
            print(f"Both fetch methods failed: {e2}")
            raise

    # Write metadata
    meta = {
        "source": "EEA Air Quality e-Reporting (E2a)",
        "download_time": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "dataset": 2,
        "countries": ["IE"],
    }
    meta_path = DATA_DIR / "fetch_metadata.json"
    meta_path.write_text(json.dumps(meta, indent=2))
    print(f"Metadata written to {meta_path}")


if __name__ == "__main__":
    main()
