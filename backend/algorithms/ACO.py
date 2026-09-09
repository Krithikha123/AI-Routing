import random
from .utils import route_distance, random_route

def ant_colony_optimization(
    matrix,
    ants=20,
    iterations=100,
    evaporation=0.5,
):
    n = len(matrix)
    pheromone = [
        [1.0 for _ in range(n)]
        for _ in range(n)
    ]
    best_route = random_route(n)
    best_distance = route_distance(best_route, matrix)
    convergence = []
    for _ in range(iterations):
        routes = []
        for _ in range(ants):
            unvisited = list(range(1,n))
            route = [0]
            while unvisited:
                current_city = route[-1]
                probabilities = []
                for next_city in unvisited:
                    pheromone_level = pheromone[current_city][next_city]
                    heuristic_value = 1.0/max(matrix[current_city][next_city], 0.001)
                    probabilities.append(pheromone_level * heuristic_value)
                total = sum(probabilities)
                probabilities = [p/total for p in probabilities]
                next_city = random.choices(unvisited, weights=probabilities)[0]
                route.append(next_city)
                unvisited.remove(next_city)
            route.append(0)
            routes.append(route)
        
        for i in range(n):
            for j in range(n):
                pheromone[i][j] *= (1 - evaporation)
        for route in routes:
            distance = route_distance(route, matrix)
            if distance < best_distance:
                best_route = route[:]
                best_distance = distance
            deposit = 1.0 / max(distance, 0.001)
            for i in range(len(route)-1):
                a = route[i]
                b = route[i+1]
                pheromone[a][b] += deposit
                pheromone[b][a] += deposit
        convergence.append(best_distance)
    return best_route, best_distance, convergence