"""Dynamic city geocoding.

City coordinates are no longer hardcoded in this project. Instead, they are
fetched from OpenStreetMap's free Nominatim geocoding API the first time a
city is needed, then cached locally in city_coords_cache.json so future
runs don't need network access or repeated API calls.

Nominatim's usage policy allows at most 1 request per second and requires
a descriptive User-Agent header, both of which are respected here.
"""

import json
import os
import time

import requests

CACHE_FILE = os.path.join(os.path.dirname(__file__), "city_coords_cache.json")
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "daa-route-optimizer-student-project/1.0"}


def _load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as cache_file:
            return json.load(cache_file)
    return {}


def _save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as cache_file:
        json.dump(cache, cache_file, indent=2)


def geocode_city(city_name, country="India"):
    """Return (lat, lng) for a city name, fetching from Nominatim if not cached."""
    cache = _load_cache()

    if city_name in cache:
        return cache[city_name]["lat"], cache[city_name]["lng"]

    params = {"q": f"{city_name}, {country}", "format": "json", "limit": 1}
    response = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=10)
    response.raise_for_status()
    results = response.json()

    if not results:
        raise ValueError(f"Could not geocode city: {city_name}")

    lat = float(results[0]["lat"])
    lng = float(results[0]["lon"])

    cache[city_name] = {"lat": lat, "lng": lng}
    _save_cache(cache)

    # Stay within Nominatim's rate limit of 1 request/second.
    time.sleep(1)

    return lat, lng


def geocode_all(city_names, country="India"):
    """Geocode a list of city names, returning {name: {"lat": .., "lng": ..}}."""
    cities = {}
    for name in city_names:
        lat, lng = geocode_city(name, country)
        cities[name] = {"lat": lat, "lng": lng}
    return cities
