let cities = [];
let currentRoute = [];
let distanceMatrix  = [];
let distanceChart = null;
let executionChart = null;
let convergenceChart = null;
let sensitivityChart = null;

const algorithmParameters = {
    "Genetic Algorithm": [
        { value: "iterations", text: "Iterations" },
        { value: "population_size", text: "Population Size" }
    ],
    "Simulated Annealing": [
        { value: "iterations", text: "Iterations" },
        { value: "initial_temperature", text: "Initial Temperature" },
        { value: "cooling_rate", text: "Cooling Rate" }
    ],
    "Ant Colony Optimization": [
        { value: "iterations", text: "Iterations" },
        { value: "ants", text: "Number of Ants" },
        { value: "evaporation", text: "Evaporation" }
    ],
    "Particle Swarm Optimization": [
        { value: "iterations", text: "Iterations" },
        { value: "particles", text: "Number of Particles" }
    ],
    "Artificial Bee Colony": [
        { value: "iterations", text: "Iterations" },
        { value: "bees", text: "Number of Bees" },
        { value: "scout_limit", text: "Scout Limit" }
    ]
};

const sensitivityDefaults = {
    iterations: "20,40,60,80,100",
    population_size: "10,20,30,40,50",
    initial_temperature: "100,300,500,700,1000",
    cooling_rate: "0.80,0.85,0.90,0.95,0.99",
    ants: "5,10,20,30,40",
    evaporation: "0.1,0.3,0.5,0.7,0.9",
    particles: "10,20,30,40,50",
    bees: "10,20,30,40,50",
    scout_limit: "5,10,15,20,25"
};

function updateSensitivityParameters() {
    const algorithmElement =
        document.getElementById("sensitivityAlgorithm");

    const parameterSelect =
        document.getElementById("sensitivityParameterSelect");

    if (!algorithmElement || !parameterSelect) {
        return;
    }

    const algorithm = algorithmElement.value;
    parameterSelect.innerHTML = "";
    const parameters = algorithmParameters[algorithm] || [];
    parameters.forEach(parameter => {
        const option = document.createElement("option");
        option.value = parameter.value;
        option.textContent = parameter.text;
        parameterSelect.appendChild(option);
    });
    updateSensitivityDefaultValues();
}

function updateSensitivityDefaultValues() {
    const parameterSelect = document.getElementById("sensitivityParameterSelect");
    const valuesInput = document.getElementById("sensitivityValues");

    if (!parameterSelect || !valuesInput) {
        return;
    }

    const parameter = parameterSelect.value;
    valuesInput.value = sensitivityDefaults[parameter] || "20,40,60,80,100";
}

document.querySelectorAll(".nav").forEach(button => {
    button.addEventListener("click", () => {
        const sectionName = button.dataset.section;

        document.querySelectorAll(".nav").forEach(item => {
            item.classList.remove("active");
        });

        document.querySelectorAll(".app-section").forEach(section => {
            section.hidden = section.dataset.section !== sectionName;
            section.classList.toggle(
                "active-section",
                !section.hidden
            );
        });

        button.classList.add("active");
    });
});

async function requestJson(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.error || `Request failed (${response.status})`
        );
    }

    return data;
}

async function generateCities() {
    const number = Number.parseInt(
        document.getElementById("cityCount").value,
        10
    );

    if (!Number.isInteger(number) || number < 2 || number > 40) {
        alert("Enter a number of cities between 2 and 40.");
        return;
    }

    try {
        const data = await requestJson("/generate_cities", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                num_cities: number
            })
        });

        cities = data.cities;
        distanceMatrix = data.matrix;
        currentRoute = [];

        displayCities();
        displayDistanceMatrix();
        drawNetwork();

        document.getElementById("distance").textContent = "-";
        document.getElementById("route").textContent = "Run an algorithm to see the optimized route.";
    } 
    catch (error) {
        alert(error.message);
        console.error(error);
    }
}

function displayCities() {
    const generatedCities =
        cities.filter(city => city.name !== "SOURCE");

    document.getElementById("cityList").innerHTML =
        generatedCities.map(city => `
            <div class="city">
                <span class="city-name">${city.name}</span>
                <span class="city-coord">
                    ${city.lat}, ${city.lon}
                </span>
            </div>
        `).join("");
}

function displayDistanceMatrix() {
    const table = document.getElementById("distanceMatrix");

    if (!table) {
        console.error("distanceMatrix table not found.");
        return;
    }

    if (!distanceMatrix.length || !cities.length) {
        table.innerHTML = `
            <tbody>
                <tr>
                    <td class="empty-matrix">
                        Generate cities to display the distance matrix.
                    </td>
                </tr>
            </tbody>
        `;
        return;
    }

    let html = "<thead><tr><th>Location</th>";

    cities.forEach(city => {
        html += `<th>${city.name}</th>`;
    });

    html += "</tr></thead><tbody>";

    distanceMatrix.forEach((row, rowIndex) => {
        html += `<tr><th>${cities[rowIndex].name}</th>`;

        row.forEach(distance => {
            html += `<td>${Number(distance).toFixed(2)}</td>`;
        });

        html += "</tr>";
    });

    html += "</tbody>";

    table.innerHTML = html;
}

function drawNetwork(route = currentRoute) {
    const canvas = document.getElementById("network");

    if (!canvas) {
        return;
    }

    const context = canvas.getContext("2d");

    canvas.width = Math.max(canvas.clientWidth, 320);
    canvas.height = 390;

    context.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    if (cities.length === 0) {
        return;
    }

    const sourceLat = 19.0760;
    const sourceLon = 72.8777;

    const latitudes =
        cities.map(city => city.lat);

    const longitudes =
        cities.map(city => city.lon);

    const minLat =
        Math.min(sourceLat - 0.5, ...latitudes);

    const maxLat =
        Math.max(sourceLat + 0.5, ...latitudes);

    const minLon =
        Math.min(sourceLon - 0.5, ...longitudes);

    const maxLon =
        Math.max(sourceLon + 0.5, ...longitudes);

    const getX = longitude =>
        50 +
        ((longitude - minLon) /
            (maxLon - minLon)) *
        (canvas.width - 100);

    const getY = latitude =>
        canvas.height -
        50 -
        ((latitude - minLat) /
            (maxLat - minLat)) *
        (canvas.height - 100);

    if (route && route.length > 1) {
        for (let i = 0; i < route.length - 1; i++) {
            const fromCity = cities[route[i]];
            const toCity = cities[route[i + 1]];

            if (!fromCity || !toCity) {
                continue;
            }

            const x1 = getX(fromCity.lon);
            const y1 = getY(fromCity.lat);

            const x2 = getX(toCity.lon);
            const y2 = getY(toCity.lat);

            context.beginPath();
            context.moveTo(x1, y1);
            context.lineTo(x2, y2);
            context.strokeStyle = "#5046e5";
            context.lineWidth = 3;
            context.stroke();

            const angle =
                Math.atan2(
                    y2 - y1,
                    x2 - x1
                );

            const arrowLength = 10;
            const arrowAngle = Math.PI / 6;

            const arrowX =
                x1 + (x2 - x1) * 0.75;

            const arrowY =
                y1 + (y2 - y1) * 0.75;

            context.beginPath();

            context.moveTo(
                arrowX,
                arrowY
            );

            context.lineTo(
                arrowX -
                arrowLength *
                Math.cos(angle - arrowAngle),
                arrowY -
                arrowLength *
                Math.sin(angle - arrowAngle)
            );

            context.moveTo(
                arrowX,
                arrowY
            );

            context.lineTo(
                arrowX -
                arrowLength *
                Math.cos(angle + arrowAngle),
                arrowY -
                arrowLength *
                Math.sin(angle + arrowAngle)
            );

            context.strokeStyle = "#5046e5";
            context.lineWidth = 2;
            context.stroke();
        }
    }

    cities.forEach((city, index) => {
        const x = getX(city.lon);
        const y = getY(city.lat);

        context.beginPath();

        context.arc(
            x,
            y,
            7,
            0,
            Math.PI * 2
        );

        context.fillStyle =
            index === 0
                ? "#20a05a"
                : "#333333";

        context.fill();

        context.fillStyle = "#182235";
        context.font = "12px Arial";

        context.fillText(
            city.name,
            x + 10,
            y + 4
        );
    });
}

async function runAlgorithm() {
    if (cities.length === 0) {
        alert("Please generate cities first.");
        return;
    }

    try {
        const data = await requestJson(
            "/run_algorithm",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    algorithm:
                        document.getElementById(
                            "algorithm"
                        ).value
                })
            }
        );

        currentRoute = data.route;

        drawNetwork(currentRoute);

        document.getElementById(
            "distance"
        ).textContent =
            `${data.distance} km`;

        document.getElementById(
            "route"
        ).innerHTML = `
            <b>${data.algorithm}</b><br>
            ${data.route_names.join(" &rarr; ")}<br>
            ${data.execution_time} seconds
        `;
    } catch (error) {
        alert(error.message);
        console.error(error);
    }
}

async function compareAlgorithms() {
    if (cities.length === 0) {
        alert("Please generate cities first.");
        return;
    }

    try {
        const data =
            await requestJson(
                "/compare_algorithms",
                {
                    method: "POST"
                }
            );

        document.querySelector(
            "#comparisonTable tbody"
        ).innerHTML =
            data.results.map(result => `
                <tr>
                    <td>${result.algorithm}</td>
                    <td>${result.distance}</td>
                    <td>${result.execution_time}</td>
                </tr>
            `).join("");

        document.getElementById(
            "comparisonConclusion"
        ).textContent = data.conclusion;

        const algorithms =
            data.results.map(
                result => result.algorithm
            );

        const distances =
            data.results.map(
                result => result.distance
            );

        const executionTimes =
            data.results.map(
                result => result.execution_time
            );

        if (distanceChart) {
            distanceChart.destroy();
        }

        if (executionChart) {
            executionChart.destroy();
        }

        if (convergenceChart) {
            convergenceChart.destroy();
        }

        distanceChart = new Chart(
            document.getElementById(
                "distanceChart"
            ),
            {
                type: "bar",

                data: {
                    labels: algorithms,

                    datasets: [{
                        label: "Distance (km)",
                        data: distances
                    }]
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,

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
                                text: "Distance (km)"
                            }
                        },

                        x: {
                            title: {
                                display: true,
                                text: "Algorithm"
                            }
                        }
                    }
                }
            }
        );

        executionChart = new Chart(
            document.getElementById(
                "executionChart"
            ),
            {
                type: "bar",

                data: {
                    labels: algorithms,

                    datasets: [{
                        label: "Execution Time (sec)",
                        data: executionTimes
                    }]
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,

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
                                text: "Time (sec)"
                            }
                        },

                        x: {
                            title: {
                                display: true,
                                text: "Algorithm"
                            }
                        }
                    }
                }
            }
        );

        const convergenceDatasets =
            data.results.map(result => ({
                label: result.algorithm,
                data: result.convergence,
                fill: false,
                tension: 0.2
            }));

        const maxIterations =
            Math.max(
                ...data.results.map(
                    result =>
                        result.convergence.length
                )
            );

        convergenceChart = new Chart(
            document.getElementById(
                "convergenceChart"
            ),
            {
                type: "line",

                data: {
                    labels: Array.from(
                        {
                            length: maxIterations
                        },
                        (_, index) => index + 1
                    ),

                    datasets:
                        convergenceDatasets
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,

                    interaction: {
                        mode: "index",
                        intersect: false
                    },

                    plugins: {
                        legend: {
                            display: true,
                            position: "bottom"
                        }
                    },

                    scales: {
                        y: {
                            title: {
                                display: true,
                                text: "Best Distance (km)"
                            }
                        },

                        x: {
                            title: {
                                display: true,
                                text: "Iteration"
                            }
                        }
                    }
                }
            }
        );
    } catch (error) {
        alert(error.message);
        console.error(error);
    }
}

async function runStatistics() {
    if (cities.length === 0) {
        alert("Please generate cities first.");
        return;
    }

    try {
        const runs =
            Number.parseInt(
                document.getElementById(
                    "runs"
                ).value,
                10
            );

        if (
            !Number.isInteger(runs) ||
            runs < 2 ||
            runs > 20
        ) {
            alert(
                "Enter number of runs between 2 and 20."
            );
            return;
        }

        const data =
            await requestJson(
                "/statistics",
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json"
                    },
                    body: JSON.stringify({
                        runs: runs
                    })
                }
            );

        document.querySelector(
            "#statisticsTable tbody"
        ).innerHTML =
            data.results.map(result => `
                <tr>
                    <td>${result.algorithm}</td>
                    <td>${result.average}</td>
                    <td>${result.best}</td>
                    <td>${result.worst}</td>
                    <td>${result.variance}</td>
                </tr>
            `).join("");
    } catch (error) {
        alert(error.message);
        console.error(error);
    }
}

async function runSensitivity() {
    if (cities.length === 0) {
        alert("Please generate cities first.");
        return;
    }

    try {
        const algorithm =
            document.getElementById(
                "sensitivityAlgorithm"
            ).value;

        const parameter =
            document.getElementById(
                "sensitivityParameterSelect"
            ).value;

        const valuesText =
            document.getElementById(
                "sensitivityValues"
            ).value;

        const values =
            valuesText
                .split(",")
                .map(value =>
                    Number(value.trim())
                )
                .filter(
                    value =>
                        !Number.isNaN(value)
                );

        if (values.length === 0) {
            alert(
                "Enter valid parameter values."
            );
            return;
        }

        const data =
            await requestJson(
                "/sensitivity",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        algorithm: algorithm,
                        parameter: parameter,
                        values: values
                    })
                }
            );

        document.querySelector(
            "#sensitivityTable tbody"
        ).innerHTML =
            data.values.map(
                (value, index) => `
                    <tr>
                        <td>${value}</td>
                        <td>${data.distances[index]}</td>
                        <td>
                            ${
                                data.execution_times
                                    ? data.execution_times[index]
                                    : "-"
                            }
                        </td>
                    </tr>
                `
            ).join("");

        if (sensitivityChart) {
            sensitivityChart.destroy();
        }

        const canvas = document.getElementById("sensitivityChart");

        const context = canvas.getContext("2d");

        sensitivityChart = new Chart(
            context,
            {
                type: "line",
                data: {labels: data.values,
                    datasets: [{label:`${data.parameter} vs Distance`,
                        data:data.distances,
                        fill: false,
                        tension: 0.2,
                        borderWidth: 2
                    }]
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,

                    interaction: {
                        mode: "index",
                        intersect: false
                    },

                    plugins: {
                        legend: {
                            display: true
                        }
                    },

                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: data.parameter
                            }
                        },

                        y: {
                            beginAtZero: false,

                            title: {
                                display: true,
                                text: "Distance (km)"
                            }
                        }
                    }
                }
            }
        );
    } catch (error) {
        alert(error.message);
        console.error(error);
    }
}

document.getElementById("sensitivityAlgorithm").addEventListener(
    "change",updateSensitivityParameters);

document.getElementById("sensitivityParameterSelect").addEventListener(
    "change",updateSensitivityDefaultValues);
updateSensitivityParameters();

window.addEventListener(
    "resize",
    () => {
        if (cities.length > 0) {
            drawNetwork();
        }
    }
);

drawNetwork();