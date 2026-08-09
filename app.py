"""Saarthi - Flask web application for intelligent route optimization."""

from flask import Flask, render_template, request

from algorithms import dijkstra, find_all_routes, sort_routes
from backend import format_route_label, visualize_map
from graph_data import CITIES, GRAPH

# This file is the main controller of Saarthi.
# It connects user input, algorithm execution, and frontend rendering.
app = Flask(__name__)

MODE_LABELS = {
    "distance": "Shortest Distance",
    "cost": "Minimum Cost",
    "balanced": "Balanced",
}


def validate_inputs(source, destination, mode, alpha_text, beta_text):
    """Validate form inputs and return cleaned values or an error message."""
    city_names = set(GRAPH.keys())

    if source not in city_names:
        return None, "Invalid source city selected."
    if destination not in city_names:
        return None, "Invalid destination city selected."
    if source == destination:
        return None, "Source and destination must be different."
    if mode not in MODE_LABELS:
        return None, "Invalid optimization mode selected."

    alpha = 1.0
    beta = 1.0

    if mode == "balanced":
        try:
            alpha = float(alpha_text)
            beta = float(beta_text)
        except (TypeError, ValueError):
            return None, "Alpha and beta must be valid numbers for balanced mode."

        if alpha < 0 or beta < 0:
            return None, "Alpha and beta must be non-negative."

        if alpha == 0 and beta == 0:
            return None, "At least one of alpha or beta must be greater than 0."

    return {
        "source": source,
        "destination": destination,
        "mode": mode,
        "alpha": alpha,
        "beta": beta,
    }, None


def build_routes(source, destination, mode, alpha, beta):
    """Run Dijkstra and DFS, then return sorted top routes and optimal route."""
    # Dijkstra finds the single best route according to the selected mode and collects step trace.
    distances, previous_nodes, optimal_path, trace_steps = dijkstra(
        GRAPH, source, destination, mode, alpha, beta, trace=True
    )

    all_routes = []
    # DFS generates all simple routes so we can compare alternatives.
    find_all_routes(
        GRAPH,
        source,
        destination,
        visited={source},
        current_path=[source],
        all_routes=all_routes,
        mode=mode,
        alpha=alpha,
        beta=beta,
    )

    sorted_routes = sort_routes(all_routes)
    top_routes = sorted_routes[:5]

    optimal_route = None
    for route in top_routes:
        if route["path"] == optimal_path:
            optimal_route = route
            break

    # If Dijkstra finds a path that is not already inside the top slice, place it first.
    if optimal_route is None and optimal_path:
        for route in sorted_routes:
            if route["path"] == optimal_path:
                optimal_route = route
                top_routes = [route] + [item for item in top_routes if item["path"] != route["path"]]
                top_routes = top_routes[:5]
                break

    selected_index = 0
    route_labels = [format_route_label(route) for route in top_routes]
    map_data = visualize_map(CITIES, top_routes, selected_index=selected_index, trace_steps=trace_steps)

    return {
        "distances": distances,
        "previous_nodes": previous_nodes,
        "optimal_path": optimal_path,
        "optimal_route": optimal_route,
        "routes": top_routes,
        "route_labels": route_labels,
        "map_data": map_data,
    }


@app.route("/", methods=["GET", "POST"])
def index():
    """Render the form and show results after the user submits a query."""
    # This route handles both the initial page load and the form submission.
    context = {
        "cities": sorted(CITIES.keys()),
        "mode_labels": MODE_LABELS,
        "selected_form": {
            "source": "",
            "destination": "",
            "mode": "distance",
            "alpha": "1",
            "beta": "1",
        },
        "error_message": None,
        "result": None,
    }

    if request.method == "POST":
        source = request.form.get("source", "").strip()
        destination = request.form.get("destination", "").strip()
        mode = request.form.get("mode", "").strip()
        alpha_text = request.form.get("alpha", "1").strip()
        beta_text = request.form.get("beta", "1").strip()

        context["selected_form"] = {
            "source": source,
            "destination": destination,
            "mode": mode,
            "alpha": alpha_text,
            "beta": beta_text,
        }

        cleaned_inputs, error_message = validate_inputs(
            source, destination, mode, alpha_text, beta_text
        )

        if error_message:
            context["error_message"] = error_message
        else:
            result = build_routes(
                cleaned_inputs["source"],
                cleaned_inputs["destination"],
                cleaned_inputs["mode"],
                cleaned_inputs["alpha"],
                cleaned_inputs["beta"],
            )
            context["result"] = result

            if result["optimal_route"] is None:
                context["error_message"] = "No route found between the selected cities."

    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(debug=True)
