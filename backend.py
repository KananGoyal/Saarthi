"""Saarthi - Backend helpers for preparing route and map data."""

# This file contains support functions that prepare clean output for display.
# It keeps formatting logic separate from both the algorithms and the Flask route.


def format_route_label(route):
    """Build a readable route label for HTML and console output."""
    if "legs" in route and route["legs"]:
        legs_str = " | ".join(
            f"{leg['from']}->{leg['to']} ({leg['mode']}: Rs.{leg['cost']})"
            for leg in route["legs"]
        )
        return (
            f"{' -> '.join(route['path'])} "
            f"(Dist: {route['total_distance']:.1f} km, Cost: Rs. {route['total_cost']}, "
            f"Score: {route['score']:.1f}) [{legs_str}]"
        )
    return (
        f"{' -> '.join(route['path'])} "
        f"(Distance: {route['total_distance']:.1f} km, Cost: Rs. {route['total_cost']}, "
        f"Score: {route['score']:.1f})"
    )


def visualize_map(cities, routes, selected_index=0, trace_steps=None):
    """Prepare JSON-ready map data. The browser handles actual drawing with Leaflet."""
    # The map is used only for visualization, not for route computation.
    route_polylines = []

    for route in routes:
        coordinates = []
        for city in route["path"]:
            coordinates.append([cities[city]["lat"], cities[city]["lng"]])
        route_polylines.append(
            {
                "path": route["path"],
                "coordinates": coordinates,
                "distance": route["total_distance"],
                "cost": route["total_cost"],
                "score": route["score"],
                "legs": route.get("legs", []),
            }
        )

    return {
        "cities": cities,
        "routes": route_polylines,
        "selected_index": selected_index if route_polylines else None,
        "trace_steps": trace_steps or [],
    }


