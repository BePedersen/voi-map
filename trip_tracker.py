import json
import os
from math import radians, cos, sin, sqrt, atan2
from datetime import datetime, timedelta

# Constants
TRIP_DISTANCE_THRESHOLD_METERS = 100
LOG_FILE_PATH = "vehicle_log.json"

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points on Earth using Haversine formula."""
    R = 6371000  # Earth radius in meters
    phi1, phi2 = radians(lat1), radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)

    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

def track_trips(bikes, city_id):
    """
    Tracks trips for scooters in a city by comparing current and previous locations.
    
    Args:
        bikes (list): List of bike dicts with 'bike_id', 'lat', 'lon'.
        city_id (str): Unique identifier for the city, e.g., 'bergen'.
        
    Returns:
        int: Number of detected trips.
    """
    if not os.path.exists(LOG_FILE_PATH):
        log_data = {}
    else:
        with open(LOG_FILE_PATH, "r") as f:
            log_data = json.load(f)

    now = datetime.utcnow().isoformat()
    city_data = log_data.get(city_id, {"vehicles": {}, "last_reset": now, "trips": 0})

    # Reset trip counter if 24 hours have passed
    last_reset = datetime.fromisoformat(city_data["last_reset"])
    if datetime.utcnow() - last_reset > timedelta(hours=24):
        city_data = {"vehicles": {}, "last_reset": now, "trips": 0}

    for bike in bikes:
        bike_id = bike["bike_id"]
        lat, lon = bike["lat"], bike["lon"]

        if bike_id in city_data["vehicles"]:
            prev = city_data["vehicles"][bike_id]
            distance = haversine_distance(lat, lon, prev["lat"], prev["lon"])
            if distance >= TRIP_DISTANCE_THRESHOLD_METERS:
                city_data["trips"] += 1

        # Update or add current position
        city_data["vehicles"][bike_id] = {"lat": lat, "lon": lon}

    log_data[city_id] = city_data

    with open(LOG_FILE_PATH, "w") as f:
        json.dump(log_data, f, indent=2)

    return city_data["trips"]
