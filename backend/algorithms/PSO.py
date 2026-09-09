import random
from .utils import route_distance, random_route
def particle_swarm_optimization(
    matrix,
    particles=20,
    iterations=100
):
    n = len(matrix)
    swarm = [random_route(n) for _ in range(particles)]
    personal_best_routes = [route[:] for route in swarm]
    personal_best_distances = [route_distance(route, matrix) for route in swarm]
    best_index = personal_best_distances.index(min(personal_best_distances))
    global_best_route = personal_best_routes[best_index][:]
    global_best_distance = personal_best_distances[best_index]
    convergence = []

    for _ in range(iterations):
        for i in range(particles):
            route = swarm[i][:]
            if random.random() < 0.7:
                pos = random.randint(1, n-1)
                if global_best_route[pos] in route:
                    target = global_best_route[pos]
                    target_pos = route.index(target)
                    route[pos], route[target_pos] = route[target_pos], route[pos]
            if random.random() < 0.3:
                a,b = random.sample(range(1,n), 2)
                route[a], route[b] = (route[b], route[a])
            swarm[i] = route
            distance = route_distance(route, matrix)
            if distance < personal_best_distances[i]:
                personal_best_routes[i] = route[:]
                personal_best_distances[i] = distance
            if distance < global_best_distance:
                global_best_route = route[:]
                global_best_distance = distance
        convergence.append(global_best_distance)
    return global_best_route, global_best_distance, convergence