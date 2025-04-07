import json
import os
import csv
from datetime import datetime, timedelta, timezone

TRIP_DISTANCE_THRESHOLD_METERS = 100
LOG_FILE_PATH = "vehicle_log.json"
TRIP_LOG_DIR = "trip_logs"

# Define GMT+2 timezone
gmt_plus_2 = timezone(timedelta(hours=2))

def track_trips(bikes, city_id):
    # Ensure log directory exists
    os.makedirs(TRIP_LOG_DIR, exist_ok=True)

    # Load or initialize log
    if not os.path.exists(LOG_FILE_PATH):
        log_data = {}
    else:
        with open(LOG_FILE_PATH, "r") as f:
            log_data = json.load(f)

    now = datetime.now(gmt_plus_2)
    today_reset_time = now.replace(hour=23, minute=0, second=0, microsecond=0)
    if now < today_reset_time:
        today_reset_time -= timedelta(days=1)  # Move to yesterday's 23:00 if current time is before it

    city_data = log_data.get(city_id, {
        "points": [],
        "last_reset": today_reset_time.isoformat(),
        "trips": 0
    })

    last_reset_dt = datetime.fromisoformat(city_data["last_reset"]).astimezone(gmt_plus_2)

    # Check if a new reset is needed
    if now >= last_reset_dt + timedelta(days=1):
        # Save previous day's trip count to CSV
        date_str = (last_reset_dt + timedelta(days=1)).strftime("%Y-%m-%d")
        csv_filename = os.path.join(TRIP_LOG_DIR, f"{city_id}_trips_{date_str}.csv")
        with open(csv_filename, "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["city", "date", "trips"])
            writer.writerow([city_id, date_str, city_data["trips"]])

        # Reset city data
        city_data = {
            "points": [],
            "last_reset": today_reset_time.isoformat(),
            "trips": 0
        }

    # Extract current [lat, lon] positions
    current_points = [[round(b["lat"], 5), round(b["lon"], 5)] for b in bikes]
    current_set = set(tuple(p) for p in current_points)
    previous_set = set(tuple(p) for p in city_data["points"])

    # Count "vanished" scooters as trips
    vanished_points = previous_set - current_set
    city_data["trips"] += len(vanished_points)

    # Save current points for next comparison
    city_data["points"] = current_points
    city_data["last_reset"] = city_data["last_reset"]  # keep existing reset time

    log_data[city_id] = city_data

    with open(LOG_FILE_PATH, "w") as f:
        json.dump(log_data, f, indent=2)

    return city_data["trips"]