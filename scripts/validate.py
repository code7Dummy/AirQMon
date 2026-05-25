import polars as pl
import os
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
VALIDATED_DIR = Path(__file__).resolve().parent.parent / "data" / "validated"
POLLUTANT_CODES = {5: "PM10", 7: "PM2.5", 8: "NO2", 6001: "O3", 1: "SO2"}
POLLUTANT_NAMES = set(POLLUTANT_CODES.values())
CODE_TO_NAME = {c: n for n, c in POLLUTANT_CODES.items()}

def main():
    VALIDATED_DIR.mkdir(parents=True, exist_ok=True)
    files = list(RAW_DIR.glob("*.parquet"))
    if not files:
        print("No raw files found. Run fetch_e2a.py first.")
        sys.exit(1)

    frames = []
    for f in files:
        try:
            df = pl.read_parquet(f)
            frames.append(df)
        except Exception as e:
            print(f"Skipping {f.name}: {e}")

    if not frames:
        print("No valid frames to process.")
        sys.exit(1)

    combined = pl.concat(frames)

    before = combined.height

    # Filter: Validity=1 only
    combined = combined.filter(pl.col("Validity") == 1)

    # Convert Decimal to float for Value and DataCapture
    combined = combined.with_columns(
        pl.col("Value").cast(pl.Float64),
        pl.when(pl.col("DataCapture").is_null()).then(None).otherwise(pl.col("DataCapture").cast(pl.Float64)).alias("DataCapture"),
    )

    # Map Pollutant code to name
    combined = combined.with_columns(
        pl.col("Pollutant").replace_strict([1, 5, 7, 8, 6001], ["SO2", "PM10", "PM2.5", "NO2", "O3"]).alias("PollutantName")
    )

    # Drop rows with null/negative values
    combined = combined.filter(
        pl.col("Value").is_not_null() & (pl.col("Value") >= 0)
    )

    # Extract AirQualityStationEoICode from Samplingpoint
    combined = combined.with_columns(
        pl.col("Samplingpoint").str.replace(r"^IE/SPO\.IE\.", "").alias("_rest")
    ).with_columns(
        pl.col("_rest").str.replace(r"Sample.+$", "").alias("AirQualityStationEoICode")
    ).drop("_rest")

    after = combined.height
    print(f"Validated: {before} -> {after} rows (dropped {before - after})")

    output_path = VALIDATED_DIR / "e2a_validated.parquet"
    combined.write_parquet(str(output_path))
    print(f"Wrote {output_path}")

    # Summary
    print("\nStations found:", combined["AirQualityStationEoICode"].n_unique())
    print("Pollutants:", sorted(combined["PollutantName"].unique().to_list()))
    print("Date range:", combined["Start"].min(), "to", combined["Start"].max())

if __name__ == "__main__":
    import sys
    main()
