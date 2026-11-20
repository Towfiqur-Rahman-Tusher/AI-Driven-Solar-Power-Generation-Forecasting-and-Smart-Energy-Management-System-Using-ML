
const API = "http://127.0.0.1:8000/api/v1/weather";

const monthNames = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
];

const charts = {};

function formatNumber(value, digits = 2) {
    if (value === null || value === undefined) return "--";
    return Number(value).toLocaleString("en-US", {
        maximumFractionDigits: digits
    });
}

async function getData(endpoint) {
    const response = await fetch(`${API}${endpoint}`);

    if (!response.ok) {
        throw new Error(`API error ${response.status}: ${await response.text()}`);
    }

    const result = await response.json();

    if (!result.success) {
        throw new Error("API returned unsuccessful response");
    }

    return result.data;
}

function drawChart(id, type, labels, datasets) {
    if (charts[id]) charts[id].destroy();

    charts[id] = new Chart(document.getElementById(id), {
        type,
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { intersect: false, mode: "index" },
            plugins: {
                legend: { display: true, position: "bottom" }
            },
            scales: {
                y: { beginAtZero: false }
            }
        }
    });
}

async function loadOverview() {
    const data = await getData("/overview");

    document.getElementById("totalRecords").textContent =
        formatNumber(data.total_records, 0);

    document.getElementById("totalLocations").textContent =
        data.total_locations;

    document.getElementById("avgTemperature").textContent =
        `${formatNumber(data.average_temperature)} °C`;

    document.getElementById("avgRadiation").textContent =
        `${formatNumber(data.average_radiation)} W/m²`;
}

async function loadLocations() {
    const locations = await getData("/locations");
    const select = document.getElementById("locationSelect");

    locations.forEach(location => {
        const option = document.createElement("option");
        option.value = location.location;
        option.textContent = location.location;
        select.appendChild(option);
    });
}

async function loadMonthly(location = "") {
    const query = location
        ? `?location=${encodeURIComponent(location)}`
        : "";

    const data = await getData(`/monthly${query}`);

    const labels = data.map(row => monthNames[row.month - 1]);

    drawChart("temperatureChart", "line", labels, [{
        label: "Average Temperature",
        data: data.map(row => row.avg_temperature),
        tension: 0.3
    }]);

    drawChart("radiationChart", "bar", labels, [{
        label: "Average Solar Radiation",
        data: data.map(row => row.avg_radiation)
    }]);
}

async function loadYearly(location = "") {
    const query = location
        ? `?location=${encodeURIComponent(location)}`
        : "";

    const data = await getData(`/yearly${query}`);
    const labels = data.map(row => row.year);

    drawChart("yearTemperatureChart", "line", labels, [{
        label: "Average Temperature",
        data: data.map(row => row.avg_temperature),
        tension: 0.3
    }]);

    drawChart("yearRadiationChart", "line", labels, [{
        label: "Average Solar Radiation",
        data: data.map(row => row.avg_radiation),
        tension: 0.3
    }]);
}

async function loadComparison() {
    const data = await getData("/comparison");

    drawChart(
        "comparisonChart",
        "bar",
        data.map(row => row.location),
        [
            {
                label: "Average Temperature (°C)",
                data: data.map(row => row.avg_temperature)
            },
            {
                label: "Average Humidity (%)",
                data: data.map(row => row.avg_humidity)
            },
            {
                label: "Average Cloud Cover (%)",
                data: data.map(row => row.avg_cloud_cover)
            }
        ]
    );

    const tbody = document.getElementById("comparisonTable");
    tbody.replaceChildren();

    data.forEach(row => {
        const tr = document.createElement("tr");

        [
            row.location,
            `${formatNumber(row.avg_temperature)} °C`,
            `${formatNumber(row.avg_radiation)} W/m²`,
            `${formatNumber(row.avg_humidity)} %`,
            `${formatNumber(row.avg_cloud_cover)} %`
        ].forEach(value => {
            const td = document.createElement("td");
            td.textContent = value;
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });
}

async function loadFeatures() {
    const data = await getData("/features");

    document.getElementById("featureRecords").textContent =
        formatNumber(data.total_records, 0);

    document.getElementById("featureColumns").textContent =
        data.total_columns;

    document.getElementById("daytimeRecords").textContent =
        data.daytime_records === null
            ? "Not available"
            : formatNumber(data.daytime_records, 0);

    const featureList = document.getElementById("featureList");
    featureList.replaceChildren();

    data.feature_columns.forEach(feature => {
        const badge = document.createElement("span");
        badge.className = "badge text-bg-primary";
        badge.textContent = feature;
        featureList.appendChild(badge);
    });
}

async function loadDashboard() {
    const status = document.getElementById("status");

    try {
        status.textContent = "Loading analytics...";

        await loadOverview();
        await loadLocations();
        await loadMonthly();
        await loadYearly();
        await loadComparison();
        await loadFeatures();

        status.textContent = "All analytics loaded successfully";
    } catch (error) {
        console.error(error);
        status.textContent = "Error: " + error.message;
        alert("Dashboard loading failed: " + error.message);
    }
}

document.getElementById("locationSelect").addEventListener(
    "change",
    async event => {
        const location = event.target.value;

        try {
            await loadMonthly(location);
            await loadYearly(location);
        } catch (error) {
            console.error(error);
            alert("Location analysis failed: " + error.message);
        }
    }
);

loadDashboard();
