import json
import os
import csv
from math import radians, cos, sin, sqrt, atan2
from datetime import datetime, timedelta, timezone

# Constants
TRIP_DISTANCE_THRESHOLD_METERS = 100
LOG_FILE_PATH = "vehicle_log.json"
TRIP_DATA_DIR = "trip_data"

# Ensure output directory exists
os.makedirs(TRIP_DATA_DIR, exist_ok=True)

# Timezone: GMT+2
gmt_plus_2 = timezone(timedelta(hours=2))

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points on Earth using Haversine formula."""
    R = 6371000  # Earth radius in meters
    phi1, phi2 = radians(lat1), radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)

    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

def save_trip_count_to_csv(city_id, date_str, trip_count):
    """Append daily trip count to a CSV file."""
    csv_path = os.path.join(TRIP_DATA_DIR, f"{city_id}_trips.csv")
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, mode="a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["date", "city", "trips"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({"date": date_str, "city": city_id, "trips": trip_count})

def get_next_reset_time(now):
    """Calculate next reset time (today at 23:00 GMT+2 or tomorrow if past)."""
    today_23 = now.replace(hour=23, minute=0, second=0, microsecond=0)
    return today_23 if now < today_23 else today_23 + timedelta(days=1)

def track_trips(bikes, city_id):
    """
    Tracks trips for scooters in a city by comparing current and previous locations.

    Args:
        bikes (list): List of bike dicts with 'vehicle_id', 'lat', 'lon'.
        city_id (str): Unique identifier for the city, e.g., 'bergen'.

    Returns:
        int: Number of detected trips.
    """
    now = datetime.now(timezone.utc).astimezone(gmt_plus_2)
    now_iso = now.isoformat()

    if os.path.exists(LOG_FILE_PATH):
        try:
            with open(LOG_FILE_PATH, "r") as f:
                log_data = json.load(f)
        except json.JSONDecodeError:
            log_data = {}
    else:
        log_data = {}

    city_data = log_data.get(city_id, {"vehicles": {}, "last_reset": now_iso, "trips": 0})

    last_reset = datetime.fromisoformat(city_data["last_reset"]).astimezone(gmt_plus_2)
    reset_time = get_next_reset_time(last_reset - timedelta(days=1))

    if now >= reset_time:
        # Save previous day's trip count to CSV
        date_str = (reset_time - timedelta(days=1)).strftime("%Y-%m-%d")
        save_trip_count_to_csv(city_id, date_str, city_data.get("trips", 0))

        # Reset counters
        city_data = {
            "vehicles": {},
            "last_reset": now_iso,
            "trips": 0
        }

    for bike in bikes:
        bike_id = bike.get("vehicle_id") or bike.get("bike_id")
        lat, lon = bike["lat"], bike["lon"]

        if not bike_id:
            continue

        if bike_id in city_data["vehicles"]:
            prev = city_data["vehicles"][bike_id]
            distance = haversine_distance(lat, lon, prev["lat"], prev["lon"])

            if distance >= TRIP_DISTANCE_THRESHOLD_METERS:
                city_data["trips"] += 1

        city_data["vehicles"][bike_id] = {"lat": lat, "lon": lon}

    log_data[city_id] = city_data

    with open(LOG_FILE_PATH, "w") as f:
        json.dump(log_data, f, indent=2)

    return city_data["trips"]