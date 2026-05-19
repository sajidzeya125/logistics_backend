from math import radians, cos, sin, asin, sqrt

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points
    on the Earth specified in decimal degrees.
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371  # Radius of Earth in kilometers
    return c * r



def calculate_route_distance(loaction: list[tuple[float, float]]) -> float:
    """
    Calculate the total distance of a route given a list of locations (latitude, longitude).
    """
    total_distance = 0.0
    for i in range(len(loaction) - 1):
        lat1, lon1 = loaction[i]
        lat2, lon2 = loaction[i + 1]
        total_distance += haversine_distance(lat1, lon1, lat2, lon2)
    return total_distance


def claculate_time_estimate(distance_km: float, average_speed_kmh: float = 40.0) -> float:
    """
    Calculate the estimated time to complete a route based on distance and average speed.
    Returns time in hours.
    """
    hours = distance_km / average_speed_kmh
    minutes = hours * 60
    return int(minutes)