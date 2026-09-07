import random,math
from .utils import route_distance, random_route

def simulated_annealing(
    matrix, 
    temperature=1000,
    cooling_rate=0.95,
    iterations=500
):
    n = len(matrix)
    current_route = random_route(n)
    current_distance = route_distance(current_route, matrix)
    best_route = current_route[:]
    best_distance = current_distance
    convergence = []
    T = temperature

    for _ in range(iterations):
        candidate_route = current_route[:]
        i, j = random.sample(range(1,n), 2)
        candidate_route[i], candidate_route[j] = candidate_route[j], candidate_route[i]
        candidate_distance = route_distance(candidate_route, matrix)
        difference = candidate_distance - current_distance
        if difference < 0 or random.random() < math.exp(-difference / max(T, 0.0001)):
            current_route = candidate_route
            current_distance = candidate_distance
        if current_distance < best_distance:
            best_route = current_route[:]
            best_distance = current_distance
        convergence.append(best_distance)
        T *= cooling_rate
    return best_route, best_distance, convergence
        