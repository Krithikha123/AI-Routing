import random
from .utils import route_distance, random_route

def artificial_bee_colony(
    matrix,
    bees=20,
    iterations=100,
):
    n = len(matrix)
    food_sources = [random_route(n) for _ in range(bees)]
    best_route = min(food_sources, key=lambda route: route_distance(route, matrix))
    best_distance = route_distance(best_route, matrix)
    convergence = []

    for _ in range(iterations):
        # Employed bees phase
        for i in range(bees):
            candidate_route = food_sources[i][:]
            a, b = random.sample(range(1,n), 2)
            candidate_route[a], candidate_route[b] = candidate_route[b], candidate_route[a]
            if route_distance(candidate_route, matrix) < route_distance(food_sources[i], matrix):
                food_sources[i] = candidate_route
        
        # Onlooker bees phase
        for _ in range(bees):
            selected_source = random.choice(food_sources)
            candidate_route = selected_source[:]
            a, b = random.sample(range(1,n), 2)
            candidate_route[a], candidate_route[b] = candidate_route[b], candidate_route[a]
            if route_distance(candidate_route, matrix) < route_distance(selected_source, matrix):
                index = food_sources.index(selected_source)
                food_sources[index] = candidate_route                       
        
        # Scout bees phase
        for i in range(bees):
            if random.random() < 0.05: 
                food_sources[i] = random_route(n)
        current_best_route = min(food_sources, key=lambda route: route_distance(route, matrix))
        current_best_distance = route_distance(current_best_route, matrix)
        if current_best_distance < best_distance:
            best_route = current_best_route[:]
            best_distance = current_best_distance
        convergence.append(best_distance)
    return best_route, best_distance, convergence