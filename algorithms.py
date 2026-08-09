"""Core DAA algorithms used by the route optimization system."""

from heapq import heappop, heappush

# This file contains the main algorithmic part of the project.
# It is the most important file for explaining the DAA logic in viva.


def get_edge_metrics(graph, from_city, to_city):
    """Return the distance, cost, and transport mode for a direct edge."""
    for edge in graph[from_city]:
        if edge["city"] == to_city:
            return edge["distance"], edge["cost"], edge.get("mode", "N/A")
    raise ValueError(f"No edge exists between {from_city} and {to_city}.")


def calculate_weight(distance, cost, mode, alpha=1.0, beta=1.0):
    """Choose the value that Dijkstra should optimize in the current mode."""
    if mode == "distance":
        return distance
    if mode == "cost":
        return cost
    return (alpha * distance) + (beta * cost)


def reconstruct_path(previous_nodes, source, destination):
    """Rebuild the best path after Dijkstra finishes."""
    path = []
    current_city = destination

    while current_city is not None:
        path.append(current_city)
        current_city = previous_nodes[current_city]

    path.reverse()

    if path and path[0] == source:
        return path
    return []


def dijkstra(graph, source, destination, mode, alpha=1.0, beta=1.0, trace=True):
    """Find the optimal route using a priority queue based Dijkstra implementation."""
    # distances keeps the best known value from the source to every city.
    distances = {city: float("inf") for city in graph}
    # previous_nodes is used later to rebuild the final optimal path.
    previous_nodes = {city: None for city in graph}
    distances[source] = 0
    # The priority queue always gives the next city with the smallest current weight.
    priority_queue = [(0, source)]
    visited = set()
    trace_steps = []

    if trace:
        print("\n--- Dijkstra Trace ---")
        print(f"Source: {source}, Destination: {destination}, Mode: {mode}")
        if mode == "balanced":
            print(f"Alpha: {alpha}, Beta: {beta}")

    while priority_queue:
        current_weight, current_node = heappop(priority_queue)

        if current_node in visited:
            continue

        visited.add(current_node)
        trace_steps.append({
            "action": "visit",
            "node": current_node,
            "weight": round(current_weight, 1),
        })

        if trace:
            print(f"\nProcessing node: {current_node}")
            print(f"Current best weight: {current_weight}")

        if current_node == destination:
            break

        for edge in graph[current_node]:
            neighbor = edge["city"]
            distance = edge["distance"]
            cost = edge["cost"]
            edge_weight = calculate_weight(distance, cost, mode, alpha, beta)
            new_weight = current_weight + edge_weight

            if trace:
                print(
                    f"Checking neighbor: {neighbor}, "
                    f"edge distance: {distance}, edge cost: {cost}, "
                    f"computed weight: {edge_weight}"
                )

            updated = new_weight < distances[neighbor]
            trace_steps.append({
                "action": "check_neighbor",
                "from": current_node,
                "to": neighbor,
                "distance": distance,
                "cost": cost,
                "edge_weight": round(edge_weight, 1),
                "new_weight": round(new_weight, 1),
                "updated": updated,
            })

            if updated:
                distances[neighbor] = new_weight
                previous_nodes[neighbor] = current_node
                heappush(priority_queue, (new_weight, neighbor))

                if trace:
                    print(
                        f"Updated {neighbor}: "
                        f"new best weight = {new_weight}, previous node = {current_node}"
                    )

    optimal_path = reconstruct_path(previous_nodes, source, destination)
    return distances, previous_nodes, optimal_path, trace_steps


def calculate_route_totals(graph, path, mode, alpha=1.0, beta=1.0):
    """Compute full totals and leg breakdowns for a completed route."""
    total_distance = 0.0
    total_cost = 0
    legs = []

    for index in range(len(path) - 1):
        from_city = path[index]
        to_city = path[index + 1]
        distance, cost, transport_mode = get_edge_metrics(graph, from_city, to_city)
        total_distance += distance
        total_cost += cost
        legs.append({
            "from": from_city,
            "to": to_city,
            "distance": round(distance, 1),
            "cost": int(cost),
            "mode": transport_mode,
        })

    clean_total_distance = round(total_distance, 1)
    clean_total_cost = int(round(total_cost))
    total_weight = calculate_weight(clean_total_distance, clean_total_cost, mode, alpha, beta)
    clean_score = round(total_weight, 1)

    return {
        "path": path,
        "total_distance": clean_total_distance,
        "total_cost": clean_total_cost,
        "score": clean_score,
        "legs": legs,
    }


def find_all_routes(
    graph,
    current_city,
    destination,
    visited,
    current_path,
    all_routes,
    mode,
    alpha=1.0,
    beta=1.0,
):
    """Use DFS/backtracking to collect every simple route between two cities."""
    if current_city == destination:
        all_routes.append(calculate_route_totals(graph, list(current_path), mode, alpha, beta))
        return

    for edge in graph[current_city]:
        neighbor = edge["city"]

        # We avoid revisiting cities so DFS only generates simple routes.
        if neighbor not in visited:
            visited.add(neighbor)
            current_path.append(neighbor)
            find_all_routes(
                graph,
                neighbor,
                destination,
                visited,
                current_path,
                all_routes,
                mode,
                alpha,
                beta,
            )
            current_path.pop()
            visited.remove(neighbor)


def sort_routes(routes):
    """Sort routes in ascending order of the active score."""
    return sorted(routes, key=lambda route: (route["score"], route["total_distance"], route["total_cost"]))
