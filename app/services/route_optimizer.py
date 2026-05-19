from typing import List
from math import radians, cos, sin, asin, sqrt
from .distance_calculator import haversine_distance


def nearest_neighbour_optimization(depo_location: tuple[float, float], unvisited_loactions: List[dict])->List[dict]:
    """
    Optimize the route using the Nearest Neighbour algorithm.
    :param depo_location: Tuple containing the latitude and longitude of the depot.
    :param unvisited_loactions: List of dictionaries containing the latitude and longitude of unvisited locations.
    :return: List of dictionaries representing the optimized route.
    """
    if not unvisited_loactions:
        return []
    current_location = depo_location
    optimized_route = []
    remaining_locations = unvisited_loactions.copy()
    sequence = 1
    
    while remaining_locations:
        nearest_distance = float('inf')
        nearest_index = 0

        for idx, location in enumerate(remaining_locations):
            distance = haversine_distance(current_location[0], current_location[1], location['latitude'], location['longitude'])
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_index = idx

        nearest_location = remaining_locations.pop(nearest_index)
        nearest_location['sequence'] = sequence
        nearest_location['distance_from_previous'] = nearest_distance
        optimized_route.append(nearest_location)
        current_location = (nearest_location['latitude'], nearest_location['longitude'])
        sequence += 1

    return optimized_route



def calculate_route_stats(locations: List[tuple[float, float]]) -> dict:
    """
    Calculate total distance and estimated time for a given route.
    :param locations: List of tuples containing the latitude and longitude of each location in the route.
    :return: Dictionary containing total distance and estimated time.
    """
    total_distance = 0.0
    for i in range(len(locations) - 1):
        lat1, lon1 = locations[i]
        lat2, lon2 = locations[i + 1]
        total_distance += haversine_distance(lat1, lon1, lat2, lon2)
    
    # Assuming an average speed of 40 km/h for delivery vehicles
    average_speed_kmh = 40.0
    travel_time = (total_distance / average_speed_kmh)*60
    stop_time = len(locations) * 5  # Assuming 5 minutes stop time at each location
    estimated_time = int(travel_time + stop_time)

    return {
        'total_distance': round(total_distance, 2),
        'estimated_time': estimated_time
    }