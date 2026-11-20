
let chart = null;

// CITY SELECTION
const citySelect = document.getElementById("city");

citySelect.addEventListener("change", function () {
    const [lat, lon] = this.value.split(",");

    document.getElementById("latitude").value = lat;
    document.getElementById("longitude").value = lon;

    document.getElementById("locationStatus").innerText =
        "Selected city: " + this.options[this.selectedIndex].text;
});

// GPS LOCATION
function useGPS() {
    const status = document.getElementById("locationStatus");

    if (!navigator.geolocation) {
        status.innerText = "GPS is not supported by this browser.";
        return;
    }

    status.innerText = "Detecting location...";

    navigator.geolocation.getCurrentPosition(
        function (position) {
            document.getElementById("latitude").value =
                position.coords.latitude.toFixed(6);

            document.getElementById("longitude").value =
                position.coords.longitude.toFixed(6);

            citySelect.value = "";

            status.innerText = "GPS location detected successfully.";
        },
        function (error) {
            status.innerText = "GPS Error: " + error.message;
        },
        {
            enableHighAccuracy: true,
            timeout: 15000
        }
    );
}

// GPS BUTTON
document.getElementById("gpsButton").addEventListener("click", useGPS);

// SOLAR FORECAST
document.getElementById("forecastForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const status = document.getElementById("status");
    const button = document.getElementById("forecastButton");

    status.innerText = "Generating forecast...";
    button.disabled = true;

    const payload = {
        latitude: Number(document.getElementById("latitude").value),
        longitude: Number(document.getElementById("longitude").value),
        panel_area: Number(document.getElementById("area").value),
        panel_efficiency: Number(document.getElementById("efficiency").value),
        panel_tilt: Number(document.getElementById("tilt").value),
        panel_azimuth: Number(document.getElementById("azimuth").value),
        inverter_capacity: Number(document.getElementById("inverter").value),
        inverter_efficiency: 0.97,
        forecast_hours: Number(document.getElementById("hours").value)
    };

    try {
        const response = await fetch(
            "http://127.0.0.1:8000/api/v1/forecast",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Forecast failed");
        }

        const result = data.forecast;
        const rows = result.hourly_forecast;

        // SUMMARY
        document.getElementById("energy").innerText =
            result.total_energy_kwh + " kWh";

        document.getElementById("power").innerText =
            result.maximum_power_kw + " kW";

        document.getElementById("duration").innerText =
            rows.length + " Hours";

        // HOURLY TABLE
        document.getElementById("forecastTable").innerHTML =
            rows.map(r => `
                <tr>
                    <td>${r.time}</td>
                    <td>${r.Temperature_C}</td>
                    <td>${r.POA_W_m2}</td>
                    <td>${r.DC_Power_kW}</td>
                    <td>${r.AC_Power_kW}</td>
                    <td>${r.Energy_kWh}</td>
                </tr>
            `).join("");

        // CHART
        if (chart) {
            chart.destroy();
        }

        chart = new Chart(
            document.getElementById("forecastChart"),
            {
                type: "line",
                data: {
                    labels: rows.map(r => r.time.slice(5, 16)),
                    datasets: [
                        {
                            label: "Predicted AC Power (kW)",
                            data: rows.map(r => r.AC_Power_kW),
                            borderWidth: 2,
                            tension: 0.3,
                            fill: false
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            display: true
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: "Power (kW)"
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: "Forecast Time"
                            }
                        }
                    }
                }
            }
        );

        status.innerText = "Forecast generated successfully!";

    } catch (error) {
        status.innerText = "Error: " + error.message;

    } finally {
        button.disabled = false;
    }
});
