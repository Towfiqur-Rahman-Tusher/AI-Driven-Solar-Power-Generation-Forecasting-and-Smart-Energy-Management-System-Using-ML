import pandas as pd
import pvlib
import requests


def generate_solar_forecast(
    latitude,
    longitude,
    panel_area=30,
    panel_efficiency=0.20,
    panel_tilt=23,
    panel_azimuth=180,
    inverter_capacity=5,
    inverter_efficiency=0.97,
    forecast_hours=48
):
    timezone = "Asia/Dhaka"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "temperature_2m",
            "wind_speed_10m",
            "shortwave_radiation"
        ],
        "forecast_days": 3,
        "timezone": timezone,
        "wind_speed_unit": "ms"
    }

    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params=params,
        timeout=30
    )
    response.raise_for_status()

    weather = response.json()["hourly"]

    df = pd.DataFrame({
        "Temperature_C": weather["temperature_2m"],
        "Wind_Speed_ms": weather["wind_speed_10m"],
        "GHI_W_m2": weather["shortwave_radiation"]
    })

    df.index = pd.DatetimeIndex(
        pd.to_datetime(weather["time"])
    ).tz_localize(timezone)

    now = pd.Timestamp.now(tz=timezone).floor("h")
    df = df.loc[df.index >= now].head(forecast_hours).copy()

    if len(df) < forecast_hours:
        raise ValueError("Insufficient weather forecast data.")

    solar_position = pvlib.solarposition.get_solarposition(
        df.index, latitude, longitude
    )

    zenith = solar_position["apparent_zenith"]
    azimuth = solar_position["azimuth"]

    erbs = pvlib.irradiance.erbs(
        df["GHI_W_m2"], zenith, df.index
    )

    irradiance = pvlib.irradiance.get_total_irradiance(
        surface_tilt=panel_tilt,
        surface_azimuth=panel_azimuth,
        solar_zenith=zenith,
        solar_azimuth=azimuth,
        dni=erbs["dni"],
        ghi=df["GHI_W_m2"],
        dhi=erbs["dhi"],
        model="isotropic"
    )

    df["POA_W_m2"] = irradiance["poa_global"].clip(lower=0)

    module_temp = pvlib.temperature.faiman(
        poa_global=df["POA_W_m2"],
        temp_air=df["Temperature_C"],
        wind_speed=df["Wind_Speed_ms"],
        u0=25,
        u1=6.84
    )

    df["Cell_Temp_C"] = pvlib.temperature.sapm_cell_from_module(
        module_temp,
        df["POA_W_m2"],
        deltaT=3
    )

    panel_capacity = panel_area * panel_efficiency

    df["DC_Power_kW"] = (
        panel_capacity
        * (df["POA_W_m2"] / 1000)
        * (1 - 0.004 * (df["Cell_Temp_C"] - 25))
    ).clip(lower=0)

    df["AC_Power_kW"] = (
        df["DC_Power_kW"] * inverter_efficiency
    ).clip(lower=0, upper=inverter_capacity)

    df["Energy_kWh"] = df["AC_Power_kW"]

    return {
        "forecast_start": str(df.index[0]),
        "forecast_end": str(df.index[-1]),
        "total_energy_kwh": round(df["Energy_kWh"].sum(), 3),
        "maximum_power_kw": round(df["AC_Power_kW"].max(), 3),
        "hourly_forecast": [
            {
                "time": str(index),
                **{
                    key: round(float(value), 3)
                    for key, value in row.items()
                }
            }
            for index, row in df.iterrows()
        ]
    }