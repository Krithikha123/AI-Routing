from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from algorithms.utils import create_distance_matrix, city_name
from algorithms.runner import run_algorithm
import os
import random
import time
import statistics

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app = Flask(__name__)
CORS(app)

app_state = {"cities": [],"matrix": []}

ALGORITHMS = [
    "Genetic Algorithm",
    "Simulated Annealing",
    "Ant Colony Optimization",
    "Particle Swarm Optimization",
    "Artificial Bee Colony"
]

SOURCE_LAT = 19.0760
SOURCE_LON = 72.8777


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def frontend_file(filename):
    return send_from_directory(FRONTEND_DIR, filename)


@app.route("/generate_cities", methods=["POST"])
def generate_cities():
    data = request.get_json(silent=True) or {}
    num_cities = data.get("num_cities", 5)
    try:
        num_cities = int(num_cities)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid number of cities."}), 400
    number = max(2, min(num_cities, 40))
    cities = [
        {
            "name": "SOURCE",
            "lat": SOURCE_LAT,
            "lon": SOURCE_LON
        }
    ]

    for i in range(1, number + 1):
        lat = SOURCE_LAT + random.uniform(-0.5, 0.5)
        lon = SOURCE_LON + random.uniform(-0.5, 0.5)

        cities.append({
            "name": city_name(i),
            "lat": round(lat, 6),
            "lon": round(lon, 6)
        })

    coordinates = [
        (city["lat"], city["lon"])
        for city in cities
    ]

    matrix = create_distance_matrix(coordinates)

    app_state["cities"] = cities
    app_state["matrix"] = matrix

    return jsonify({
        "cities": cities,
        "matrix": matrix
    })


@app.route("/run_algorithm", methods=["POST"])
def run():
    data = request.get_json(silent=True) or {}

    algorithm_name = data.get("algorithm")

    if not algorithm_name:
        return jsonify({
            "error": "Algorithm is required."
        }), 400

    if algorithm_name not in ALGORITHMS:
        return jsonify({
            "error": "Invalid algorithm."
        }), 400

    if not app_state["matrix"]:
        return jsonify({
            "error": "No cities generated yet."
        }), 400

    start_time = time.perf_counter()

    route, distance, convergence = run_algorithm(
        algorithm_name,
        app_state["matrix"]
    )

    end_time = time.perf_counter()

    execution_time = end_time - start_time

    route_names = [
        app_state["cities"][i]["name"]
        for i in route
    ]

    return jsonify({
        "algorithm": algorithm_name,
        "route": route,
        "route_names": route_names,
        "distance": distance,
        "convergence": convergence,
        "execution_time": round(execution_time, 6)
    })


@app.route("/compare_algorithms", methods=["POST"])
def compare():
    if not app_state["matrix"]:
        return jsonify({
            "error": "Generate cities first"
        }), 400

    results = []

    for algorithm in ALGORITHMS:
        start_time = time.perf_counter()

        route, distance, convergence = run_algorithm(
            algorithm,
            app_state["matrix"]
        )

        end_time = time.perf_counter()

        execution_time = end_time - start_time

        route_names = [
            app_state["cities"][i]["name"]
            for i in route
        ]

        results.append({
            "algorithm": algorithm,
            "route": route,
            "route_names": route_names,
            "distance": distance,
            "execution_time": round(execution_time, 6),
            "convergence": convergence
        })

    best_distance = min(
        results,
        key=lambda x: x["distance"]
    )

    fastest = min(
        results,
        key=lambda x: x["execution_time"]
    )

    conclusion = (
        f"{best_distance['algorithm']} produced "
        f"the shortest route ({best_distance['distance']} km). "
        f"{fastest['algorithm']} had the lowest "
        f"execution time ({fastest['execution_time']} seconds)."
    )

    return jsonify({
        "results": results,
        "conclusion": conclusion
    })


@app.route("/sensitivity", methods=["POST"])
def sensitivity():
    data = request.get_json(silent=True) or {}

    algorithm = data.get("algorithm")
    parameter = data.get("parameter")
    values = data.get("values")

    if not algorithm:
        return jsonify({
            "error": "Algorithm is required."
        }), 400

    if algorithm not in ALGORITHMS:
        return jsonify({
            "error": "Invalid algorithm."
        }), 400

    if not parameter:
        return jsonify({
            "error": "Parameter is required."
        }), 400

    if not isinstance(values, list) or len(values) == 0:
        return jsonify({
            "error": "Parameter values are required."
        }), 400

    if not app_state["matrix"]:
        return jsonify({
            "error": "Generate cities first"
        }), 400

    allowed_parameters = {
        "Genetic Algorithm": [
            "iterations",
            "population_size"
        ],
        "Simulated Annealing": [
            "iterations",
            "initial_temperature",
            "cooling_rate"
        ],
        "Ant Colony Optimization": [
            "iterations",
            "ants",
            "evaporation"
        ],
        "Particle Swarm Optimization": [
            "iterations",
            "particles"
        ],
        "Artificial Bee Colony": [
            "iterations",
            "bees",
            "scout_limit"
        ]
    }

    if parameter not in allowed_parameters[algorithm]:
        return jsonify({
            "error": (
                f"{parameter} is not a valid parameter "
                f"for {algorithm}."
            )
        }), 400

    parameter_names = {
        "iterations": "Iterations",
        "population_size": "Population Size",
        "initial_temperature": "Initial Temperature",
        "cooling_rate": "Cooling Rate",
        "ants": "Number of Ants",
        "evaporation": "Evaporation",
        "particles": "Number of Particles",
        "bees": "Number of Bees",
        "scout_limit": "Scout Limit"
    }

    distances = []
    execution_times = []

    for value in values:
        try:
            value = float(value)

            if value.is_integer():
                value = int(value)

        except (TypeError, ValueError):
            return jsonify({
                "error": f"Invalid parameter value: {value}"
            }), 400

        params = {}

        if algorithm == "Genetic Algorithm":
            if parameter == "iterations":
                params["generations"] = int(value)

            elif parameter == "population_size":
                params["population_size"] = int(value)

        elif algorithm == "Simulated Annealing":
            if parameter == "iterations":
                params["iterations"] = int(value)

            elif parameter == "initial_temperature":
                params["temperature"] = float(value)

            elif parameter == "cooling_rate":
                params["cooling_rate"] = float(value)

        elif algorithm == "Ant Colony Optimization":
            if parameter == "iterations":
                params["iterations"] = int(value)

            elif parameter == "ants":
                params["ants"] = int(value)

            elif parameter == "evaporation":
                params["evaporation"] = float(value)

        elif algorithm == "Particle Swarm Optimization":
            if parameter == "iterations":
                params["iterations"] = int(value)

            elif parameter == "particles":
                params["particles"] = int(value)

        elif algorithm == "Artificial Bee Colony":
            if parameter == "iterations":
                params["iterations"] = int(value)

            elif parameter == "bees":
                params["bees"] = int(value)

            elif parameter == "scout_limit":
                params["scout_limit"] = int(value)

        start_time = time.perf_counter()

        _, distance, _ = run_algorithm(
            algorithm,
            app_state["matrix"],
            params
        )

        end_time = time.perf_counter()

        execution_time = end_time - start_time

        distances.append(round(distance, 4))
        execution_times.append(
            round(execution_time, 6)
        )

    return jsonify({
        "algorithm": algorithm,
        "parameter": parameter_names[parameter],
        "values": values,
        "distances": distances,
        "execution_times": execution_times
    })


@app.route("/statistics", methods=["POST"])
def statistical_analysis():
    data = request.get_json(silent=True) or {}

    if not app_state["matrix"]:
        return jsonify({
            "error": "Generate cities first"
        }), 400

    try:
        runs = int(data.get("runs", 10))
    except (TypeError, ValueError):
        return jsonify({
            "error": "Invalid number of runs."
        }), 400

    if runs < 2 or runs > 20:
        return jsonify({
            "error": "Runs must be between 2 and 20."
        }), 400

    all_results = []

    for algorithm in ALGORITHMS:
        distances = []

        for _ in range(runs):
            _, distance, _ = run_algorithm(
                algorithm,
                app_state["matrix"]
            )

            distances.append(distance)

        average = statistics.mean(distances)
        variance = statistics.pvariance(distances)

        all_results.append({
            "algorithm": algorithm,
            "average": round(average, 2),
            "best": round(min(distances), 2),
            "worst": round(max(distances), 2),
            "variance": round(variance, 2)
        })

    return jsonify({
        "results": all_results
    })


if __name__ == "__main__":
    app.run(
        debug=True,
        port=5000
    )