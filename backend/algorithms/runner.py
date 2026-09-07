from .GA import genetic_algorithm
from .SA import simulated_annealing
from .ACO import ant_colony_optimization
from .PSO import particle_swarm_optimization
from .ABC import artificial_bee_colony

def run_algorithm(algorithm_name, matrix, params=None):
    if params is None:
        params = {}

    if algorithm_name == "Genetic Algorithm":
        return genetic_algorithm(
            matrix,
            population_size=params.get("population_size", 30),
            generations=params.get("generations", 100),
            mutation_rate=params.get("mutation_rate", 0.1)
        )

    elif algorithm_name == "Simulated Annealing":
        return simulated_annealing(
            matrix,
            temperature=params.get("temperature", 1000),
            cooling_rate=params.get("cooling_rate", 0.95),
            iterations=params.get("iterations", 500)
        )

    elif algorithm_name == "Ant Colony Optimization":
        return ant_colony_optimization(
            matrix,
            ants=params.get("ants", 20),
            iterations=params.get("iterations", 100),
            evaporation=params.get("evaporation", 0.5)
        )

    elif algorithm_name == "Particle Swarm Optimization":
        return particle_swarm_optimization(
            matrix,
            particles=params.get("particles", 20),
            iterations=params.get("iterations", 100)
        )

    elif algorithm_name == "Artificial Bee Colony":
        return artificial_bee_colony(
            matrix,
            bees=params.get("bees", 20),
            iterations=params.get("iterations", 100)
        )

    else:
        raise ValueError("Invalid algorithm")