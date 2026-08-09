# Saarthi

**Your guide to the optimal path.**

Saarthi is a route optimization engine that finds the best way to travel between Indian cities — by distance, by cost, or by a balanced mix of both — using graph algorithms and real geographic data. The name comes from Sanskrit **सारथी (Saarthi)**, meaning "charioteer" or "guide" — the one who navigates you to the right path.

---

## What it does

- **Optimizes for what matters to you** — shortest distance, lowest cost, or a custom balance between the two (adjustable via live sliders).
- **Computes real distances**, not approximations — city coordinates are fetched from OpenStreetMap and distances are calculated with the haversine formula, so numbers reflect actual geography.
- **Models realistic travel costs** across bus, train, and flight, based on distance-tiered fare rates, since no free public API exposes real-time fares.
- **Shows you alternatives, not just one answer** — ranks the top 5 route options so you can see the trade-offs, not just trust a single black-box result.
- **Visualizes the algorithm live** — watch Dijkstra explore the graph node-by-node on an interactive map, instead of a black box producing an answer.

---

## How it works

Under the hood, cities are modeled as a weighted graph, where each edge carries both a distance and a cost.

- **Dijkstra's algorithm** (priority-queue based) finds the single optimal route for whichever metric you're optimizing — O((V + E) log V).
- **DFS-based backtracking** explores alternative simple paths between source and destination, so you can compare the optimal route against realistic alternatives, not just take one answer on faith.
- **Nominatim (OpenStreetMap)** geocodes city names into real coordinates on first run, cached locally so the app runs offline afterward.

---

## Project structure

| File | What it does |
|---|---|
| `app.py` | Flask app — routes, request handling |
| `algorithms.py` | Dijkstra, DFS route enumeration, route scoring/ranking |
| `graph_data.py` | Graph construction, geocoding integration, transport-cost modeling |
| `geocoding.py` | OpenStreetMap/Nominatim integration with local caching |
| `geo_utils.py` | Haversine distance calculation |
| `backend.py` | Route formatting, map data prep |
| `templates/index.html` | UI — route input, results, live map animation |
| `static/style.css` | Styling |

---

## Running it locally

```bash
git clone https://github.com/KananGoyal/Saarthi.git
cd Saarthi
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000`.

> First run needs internet access to geocode cities via OpenStreetMap. After that, coordinates are cached locally and it runs offline.

---

## Notes on the cost model

Real-time train/bus/flight fare data isn't available through any free public API (IRCTC in particular has no open API), so Saarthi models cost using distance-tiered rates instead of live pricing:

- Bus (< 150 km): ~₹1.8/km
- Train (150–500 km): ~₹1.5/km
- Flight (> 500 km): ₹2,000 base + ₹5/km

This keeps the cost comparison realistic and explainable, while leaving room to plug in a real pricing API later.

---

## License

MIT