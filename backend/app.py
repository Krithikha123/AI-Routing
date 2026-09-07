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

app_state = {"cities": [], "matrix": []}

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
    data = request.get_json()
    num_cities = data.get("num_cities", 5)
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
    algorithm_name = data["algorithm"]

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
    algorithm = data["algorithm"]

    if not app_state["matrix"]:
        return jsonify({
            "error": "Generate cities first"
        }), 400

    parameter_values = {
        "Genetic Algorithm": [10, 20, 30, 40, 50],
        "Simulated Annealing": [0.80, 0.85, 0.90, 0.95, 0.99],
        "Ant Colony Optimization": [0.1, 0.3, 0.5, 0.7, 0.9],
        "Particle Swarm Optimization": [10, 20, 30, 40, 50],
        "Artificial Bee Colony": [10, 20, 30, 40, 50]
    }

    values = parameter_values[algorithm]
    distances = []

    for value in values:
        if algorithm == "Genetic Algorithm":
            params = {
                "population_size": value
            }
        elif algorithm == "Simulated Annealing":
            params = {
                "cooling_rate": value
            }
        elif algorithm == "Ant Colony Optimization":
            params = {
                "evaporation": value
            }
        elif algorithm == "Particle Swarm Optimization":
            params = {
                "particles": value
            }
        else:
            params = {
                "bees": value
            }

        _, distance, _ = run_algorithm(
            algorithm,
            app_state["matrix"],
            params
        )

        distances.append(distance)

    parameter_names = {
        "Genetic Algorithm": "Population Size",
        "Simulated Annealing": "Cooling Rate",
        "Ant Colony Optimization": "Evaporation",
        "Particle Swarm Optimization": "Number of Particles",
        "Artificial Bee Colony": "Number of Bees"
    }

    return jsonify({
        "parameter": parameter_names[algorithm],
        "values": values,
        "distances": distances
    })


@app.route("/statistics", methods=["POST"])
def statistical_analysis():
    data = request.get_json(silent=True) or {}

    if not app_state["matrix"]:
        return jsonify({
            "error": "Generate cities first"
        }), 400

    runs = int(data.get("runs", 10))
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