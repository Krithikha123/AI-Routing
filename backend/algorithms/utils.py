import math,random

def distance(city1, city2):
    lat1, lon1 = city1
    lat2, lon2 = city2
    R=6371
    lat1=math.radians(lat1)
    lat2=math.radians(lat2) 
    dlat=math.radians(lat2-lat1)
    dlon=math.radians(lon2-lon1)
    a=(
        math.sin(dlat/2)**2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    )
    c=2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R*c

def create_distance_matrix(cities):
    n = len(cities)
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] = round(distance(cities[i], cities[j]), 2)
    return matrix

def route_distance(route, matrix):
    total = 0
    for i in range(len(route)-1):
        total += matrix[route[i]][route[i+1]]
    return round(total, 2)

def random_route(n):
    route = list(range(1,n))
    random.shuffle(route)
    return [0] + route + [0]

def city_name(index):
    if index == 0:
        return "SOURCE"
    index -= 1
    name = ""
    while index >= 0:
        name = chr(index % 26 + 65) + name
        index = index // 26 - 1
    return name
