import random
from .utils import random_route, route_distance

def genetic_algorithm(
    matrix, 
    population_size=30, 
    generations=100,
    mutation_rate=0.1
):
    n = len(matrix)
    population = [random_route(n) for _ in range(population_size)]
    best_route = min(population, key=lambda route: route_distance(route, matrix))
    best_distance = route_distance(best_route, matrix)
    convergence = []

    for _ in range(generations):
        population.sort(key = lambda route: route_distance(route, matrix))
        new_population = population[:2]
        while len(new_population) < population_size:
            parent1 = random.choice(population[:10])
            parent2 = random.choice(population[:10])
            start = random.randint(1, n - 2)
            end = random.randint(start, n - 1)
            child = [0] + [None] * (n - 1) + [0]
            child[start:end] = parent1[start:end]
            remaining = [
                x for x in parent2[1:-1] 
                if x not in child
            ]
            position = 1
            for value in remaining:
                while child[position] is not None:
                    position += 1
                child[position] = value
            if random.random() < mutation_rate:
                i, j = random.sample(range(1, n), 2)
                child[i], child[j] = child[j], child[i]
            new_population.append(child)
        population = new_population
        current_best_route = min(population, key=lambda route: route_distance(route, matrix))
        current_best_distance = route_distance(current_best_route, matrix)
        if current_best_distance < best_distance:
            best_route = current_best_route[:]
            best_distance = current_best_distance
        convergence.append(best_distance)
    return best_route, best_distance, convergence