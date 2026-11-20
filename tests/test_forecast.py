
import requests
import math

API_URL = "http://127.0.0.1:8000/api/v1/forecast"

BASE_PAYLOAD = {
    "latitude": 22.3569,
    "longitude": 91.7832,
    "panel_area": 30,
    "panel_efficiency": 0.20,
    "panel_tilt": 23,
    "panel_azimuth": 180,
    "inverter_capacity": 5.1,
    "inverter_efficiency": 0.97,
}


def run_test(hours):
    payload = {**BASE_PAYLOAD, "forecast_hours": hours}

    response = requests.post(API_URL, json=payload, timeout=120)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["success"] is True

    forecast = data["forecast"]
    rows = forecast["hourly_forecast"]

    # 1. Forecast duration
    assert len(rows) == hours, f"Expected {hours}, got {len(rows)}"
    print(f"PASS: {hours}-hour forecast")

    # 2. Inverter power limit
    max_power = max(float(row["AC_Power_kW"]) for row in rows)
    assert max_power <= 5.1 + 0.001
    print("PASS: Inverter power limit")

    # 3. Energy calculation
    calculated_energy = sum(
        float(row["Energy_kWh"]) for row in rows
    )
    reported_energy = float(forecast["total_energy_kwh"])

    assert math.isclose(
        calculated_energy,
        reported_energy,
        rel_tol=0.001,
        abs_tol=0.01
    )
    print("PASS: Total energy calculation")

    # 4. Nighttime generation
    for row in rows:
        hour = int(row["time"][11:13])

        if hour in [0, 1, 2, 3, 4, 21, 22, 23]:
            power = float(row["AC_Power_kW"])
            assert power <= 0.01, (
                f"Unexpected nighttime power: {row}"
            )

    print("PASS: Nighttime power check")
    print(f"Total Energy: {reported_energy:.3f} kWh")
    print(f"Maximum AC Power: {max_power:.3f} kW")
    print("-" * 40)


if __name__ == "__main__":
    print("SOLAR FORECAST SYSTEM TEST")
    print("=" * 40)

    run_test(24)
    run_test(48)

    print("ALL TESTS PASSED")
