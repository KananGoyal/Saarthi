"""Saarthi - City and route dataset for the route optimization system."""

from geocoding import geocode_all
from geo_utils import haversine_distance

CITY_NAMES = [
    "Delhi", "Jaipur", "Agra", "Lucknow", "Bhopal",
    "Indore", "Kanpur", "Gwalior", "Varanasi", "Udaipur", "Pune",
]

# Transport mode rates & thresholds (Realistic Indian transport averages)
# - BUS: Short distance (< 150 km), ~Rs. 1.8 / km
# - TRAIN: Medium distance (150 km - 500 km), ~Rs. 1.5 / km (Express/3AC avg)
# - FLIGHT: Long distance (> 500 km), Base fare Rs. 2,000 + Rs. 5.0 / km

BUS_THRESHOLD_KM = 150
TRAIN_THRESHOLD_KM = 500

BUS_RATE_PER_KM = 1.8
TRAIN_RATE_PER_KM = 1.5
FLIGHT_BASE_FARE = 2000
FLIGHT_RATE_PER_KM = 5.0


def calculate_cost_and_mode(distance):
    """Determine primary transport mode and calculate edge cost based on distance."""
    if distance < BUS_THRESHOLD_KM:
        mode = "Bus"
        cost = distance * BUS_RATE_PER_KM
    elif distance <= TRAIN_THRESHOLD_KM:
        mode = "Train"
        cost = distance * TRAIN_RATE_PER_KM
    else:
        mode = "Flight"
        cost = FLIGHT_BASE_FARE + (distance * FLIGHT_RATE_PER_KM)
    return int(round(cost)), mode


# Topologically connected city pairs (edges).
# Costs and distances are no longer hardcoded; they are computed dynamically below.
EDGES = [
    ("Delhi", "Jaipur"),
    ("Delhi", "Agra"),
    ("Delhi", "Lucknow"),
    ("Delhi", "Gwalior"),
    ("Jaipur", "Agra"),
    ("Jaipur", "Indore"),
    ("Jaipur", "Udaipur"),
    ("Agra", "Lucknow"),
    ("Agra", "Bhopal"),
    ("Agra", "Gwalior"),
    ("Lucknow", "Kanpur"),
    ("Lucknow", "Bhopal"),
    ("Lucknow", "Varanasi"),
    ("Bhopal", "Indore"),
    ("Bhopal", "Gwalior"),
    ("Bhopal", "Udaipur"),
    ("Indore", "Kanpur"),
    ("Indore", "Udaipur"),
    ("Kanpur", "Varanasi"),
    ("Indore", "Pune"),
    ("Bhopal", "Pune"),
    ("Udaipur", "Pune"),
]

# Dynamically fetched (and locally cached) real-world coordinates.
CITIES = geocode_all(CITY_NAMES)

# Build the undirected adjacency-list graph with real, computed distances and transport costs.
GRAPH = {name: [] for name in CITY_NAMES}

for city_a, city_b in EDGES:
    distance = haversine_distance(
        CITIES[city_a]["lat"], CITIES[city_a]["lng"],
        CITIES[city_b]["lat"], CITIES[city_b]["lng"],
    )
    cost, mode = calculate_cost_and_mode(distance)
    GRAPH[city_a].append({"city": city_b, "distance": distance, "cost": cost, "mode": mode})
    GRAPH[city_b].append({"city": city_a, "distance": distance, "cost": cost, "mode": mode})

