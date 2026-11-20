
from pathlib import Path
from functools import lru_cache

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]

MASTER_FILE = (
    PROJECT_ROOT / "dataset" / "raw" / "weather"
    / "bangladesh_weather_master.csv"
)

FEATURE_FILE = (
    PROJECT_ROOT / "dataset" / "raw" / "weather"
    / "bangladesh_weather_features.csv"
)


@lru_cache(maxsize=1)
def load_master():
    if not MASTER_FILE.exists():
        raise FileNotFoundError(f"Master dataset not found: {MASTER_FILE}")

    df = pd.read_csv(MASTER_FILE, parse_dates=["time"])

    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month

    return df


@lru_cache(maxsize=1)
def load_features():
    if not FEATURE_FILE.exists():
        raise FileNotFoundError(f"Feature dataset not found: {FEATURE_FILE}")

    return pd.read_csv(FEATURE_FILE, parse_dates=["time"])


def overview():
    df = load_master()

    return {
        "total_records": int(len(df)),
        "total_locations": int(df["location"].nunique()),
        "start_date": str(df["time"].min()),
        "end_date": str(df["time"].max()),
        "missing_values": int(df.isna().sum().sum()),
        "locations": sorted(df["location"].unique().tolist()),
        "average_temperature": round(float(df["temperature_2m"].mean()), 2),
        "average_humidity": round(float(df["relative_humidity_2m"].mean()), 2),
        "average_radiation": round(float(df["shortwave_radiation"].mean()), 2),
        "average_cloud_cover": round(float(df["cloud_cover"].mean()), 2),
    }


def location_list():
    df = load_master()

    result = (
        df.groupby("location")
        .agg(
            records=("time", "count"),
            latitude=("latitude", "first"),
            longitude=("longitude", "first"),
            avg_temperature=("temperature_2m", "mean"),
            avg_radiation=("shortwave_radiation", "mean"),
            avg_humidity=("relative_humidity_2m", "mean"),
        )
        .reset_index()
    )

    return result.round(2).to_dict(orient="records")


def monthly_analysis(location=None):
    df = load_master()

    if location:
        df = df[df["location"].str.lower() == location.lower()]

        if df.empty:
            raise ValueError("Location not found")

    result = (
        df.groupby("month")
        .agg(
            avg_temperature=("temperature_2m", "mean"),
            avg_radiation=("shortwave_radiation", "mean"),
            avg_humidity=("relative_humidity_2m", "mean"),
            avg_cloud_cover=("cloud_cover", "mean"),
            total_precipitation=("precipitation", "sum"),
        )
        .reset_index()
    )

    return result.round(2).to_dict(orient="records")


def yearly_analysis(location=None):
    df = load_master()

    if location:
        df = df[df["location"].str.lower() == location.lower()]

        if df.empty:
            raise ValueError("Location not found")

    result = (
        df.groupby("year")
        .agg(
            avg_temperature=("temperature_2m", "mean"),
            avg_radiation=("shortwave_radiation", "mean"),
            avg_humidity=("relative_humidity_2m", "mean"),
            avg_cloud_cover=("cloud_cover", "mean"),
            total_precipitation=("precipitation", "sum"),
        )
        .reset_index()
    )

    return result.round(2).to_dict(orient="records")


def location_comparison():
    df = load_master()

    result = (
        df.groupby("location")
        .agg(
            avg_temperature=("temperature_2m", "mean"),
            avg_radiation=("shortwave_radiation", "mean"),
            avg_humidity=("relative_humidity_2m", "mean"),
            avg_cloud_cover=("cloud_cover", "mean"),
            total_precipitation=("precipitation", "sum"),
        )
        .reset_index()
    )

    return result.round(2).to_dict(orient="records")


def feature_analysis():
    df = load_features()

    feature_columns = [
        "year", "month", "day", "hour",
        "day_of_year", "day_of_week",
        "hour_sin", "hour_cos",
        "month_sin", "month_cos",
        "is_daytime",
    ]

    available = [col for col in feature_columns if col in df.columns]

    return {
        "total_records": int(len(df)),
        "total_columns": int(len(df.columns)),
        "feature_columns": available,
        "locations": sorted(df["location"].dropna().unique().tolist()),
        "daytime_records": (
            int(df["is_daytime"].sum())
            if "is_daytime" in df.columns else None
        ),
    }
