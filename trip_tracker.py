import json
import os
from datetime import datetime, timedelta

# Constants
LOG_FILE_PATH = "vehicle_log.json"

def round_coord(coord, precision=5):
    """Round coordinate to reduce floating-point errors and noise."""
    return round(coord, precision)

def load_log_data():
    """Load log data from file or initialize a new structure."""
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_log_data(data):
    """Save log data to file."""
    with open(LOG_FILE_PATH, "w") as f:
        json.dump(data, f, indent=2)

def track_trips_by_locations(bikes, city_id):
    """
    Count trips based on the disappearance of scooter coordinates.
    A trip is counted if a lat/lon pair from the last check no longer exists.
    """
    now = datetime.utcnow().isoformat()
    log_data = load_log_data()

    city_data = log_data.get(city_id, {
        "points": [],       # list of [lat, lon]
        "last_reset": now,
        "trips": 0
    })

    last_reset = datetime.fromisoformat(city_data["last_reset"])
    if datetime.utcnow() - last_reset > timedelta(hours=24):
        city_data = {
            "points": [],
            "last_reset": now,
            "trips": 0
        }

    previous_points = set(tuple(p) for p in city_data["points"])
    current_points = set((round_coord(b["lat"]), round_coord(b["lon"])) for b in bikes)

    disappeared = previous_points - current_points
    new_trips = len(disappeared)

    city_data["trips"] += new_trips
    city_data["points"] = [list(p) for p in current_points]
    log_data[city_id] = city_data

    save_log_data(log_data)

    return city_data["trips"]