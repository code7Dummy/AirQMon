import os, sys, tempfile, shutil
from pathlib import Path
from airbase import AirbaseClient, Dataset

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
POLLUTANTS = ["PM10", "PM2.5", "NO2", "O3", "SO2"]

def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    client = AirbaseClient()
    req = client.request(
        Dataset.Unverified,
        "IE",
        poll=POLLUTANTS,
        verbose=True,
    )

    tmp = Path(tempfile.mkdtemp())
    try:
        req.download(str(tmp))
        ie_dir = tmp / "IE"
        if ie_dir.is_dir():
            for f in ie_dir.iterdir():
                if f.suffix == ".parquet":
                    shutil.copy2(f, RAW_DIR / f.name)
        files = list(RAW_DIR.glob("*.parquet"))
        print(f"Fetched {len(files)} Parquet files to {RAW_DIR}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    main()
