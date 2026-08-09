"""Geographic distance calculation.

Distances between cities are no longer hardcoded. They are computed here
from real latitude/longitude coordinates using the haversine formula,
which gives the great-circle (straight-line) distance between two points
on Earth's surface.
"""

from math import radians, sin, cos, sqrt, atan2

EARTH_RADIUS_KM = 6371


def haversine_distance(lat1, lng1, lat2, lng2):
    """Return the great-circle distance in km between two lat/lng points."""
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return round(EARTH_RADIUS_KM * c, 1)
