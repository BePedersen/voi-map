import importlib.util
import os
from datetime import datetime

# Define cities and their Python script filenames
cities_info = [
    {"slug": "bergen", "city": "Bergen", "file": "voi-bergen.py"},    
    {"slug": "oslo", "city": "Oslo", "file": "voi-oslo.py"},    
    {"slug": "stavanger", "city": "Stavanger", "file": "voi-stavanger.py"},
    {"slug": "trondheim", "city": "Trondheim", "file": "voi-trondheim.py"},
    {"slug": "kristiansand", "city": "Kristiansand", "file": "voi-kristiansand.py"},
    {"slug": "lillestrom", "city": "Lillestrøm", "file": "voi-lillestrom.py"},
    {"slug": "moss", "city": "Moss", "file": "voi-moss.py"},
]

def render_battery_bar(percent):
    filled_width = int(percent)
    return f"""
    <div style='display: inline-block; vertical-align: middle; margin-left: 8px;'>
        <div style="
            width: 80px;
            height: 20px;
            border: 2px solid #2ecc71;
            border-radius: 4px;
            background-color: #2c3e50;
            position: relative;
            box-sizing: border-box;
        ">
            <div style="
                width: {filled_width}%;
                height: 100%;
                background-color: #2ecc71;
                border-radius: 2px;
            "></div>
        </div>
        <div style="font-weight: bold; margin-top: 4px; color: #ecf0f1; text-align: center;">{percent:.0f}%</div>
    </div>
    """

def import_city_data(py_file):
    try:
        module_name = os.path.splitext(py_file)[0]
        spec = importlib.util.spec_from_file_location(module_name, py_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return {
            "total": module.total_scooters,
            "availability": (module.available_scooters / module.total_scooters) * 100 if module.total_scooters else 0,
            "broken": module.red_count,
            "avg_battery": module.average_battery_percent if hasattr(module, "average_battery_percent") else 0,
            "trips_today": module.trips_today,


        }
    except Exception as e:
        print(f"⚠️ Could not import {py_file}: {e}")
        return {
            "total": 0,
            "availability": 0,
            "broken": 0,
            "avg_battery": 0,
            "trips_today": 0,
        }

from datetime import datetime, timedelta, timezone
gmt_plus_2 = timezone(timedelta(hours=2))
timestamp = datetime.now(gmt_plus_2).strftime("%-d.%-m.%Y, %H:%M:%S")

buttons_html = ""
for city in cities_info:
    data = import_city_data(city["file"])
    battery_bar = render_battery_bar(data["avg_battery"])
    buttons_html += f"""
    <a href="voi-{city['slug']}.html" style="
        display: block;
        text-decoration: none;
        color: #ecf0f1;
        background: #34495e;
        padding: 24px 30px;
        margin: 16px auto;
        border-radius: 14px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.3);
        font-family: 'Segoe UI', sans-serif;
        font-size: 18px;
        font-weight: 500;
        max-width: 900px;
        width: 95%;
        transition: all 0.2s ease;
    " onmouseover="this.style.background='#3c5d75'" onmouseout="this.style.background='#34495e'">
        <div style="font-size: 22px; font-weight: 600; margin-bottom: 10px;">{city['city']}</div>
        <div style="display: flex; flex-wrap: wrap; gap: 20px; align-items: center; justify-content: space-between; font-size: 18px; font-weight: bold;">
            <span>🛴 {data['total']}</span>
            <span>Availability: {data['availability']:.1f}%</span>
            <span style="color:#e74c3c;">❌ {data['broken']} unavailable</span>
            <span style="color:#e74c3c;">❌ {data['trips_today']} Trips Today</span>

            <span style="display: flex; align-items: center;">Fleet Battery Level: {battery_bar}</span>
        </div>
    </a>
    """

html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>VOI Fleet Dashboard – Norway</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="300">
    <style>
        body {{
            background-color: #1e272e;
            color: #ecf0f1;
            margin: 0;
            padding: 40px 20px;
            font-family: 'Segoe UI', sans-serif;
        }}
        h1 {{
            text-align: center;
            font-size: 28px;
            margin-bottom: 40px;
        }}
        .timestamp {{
            text-align: center;
            margin-top: 40px;
            color: #bdc3c7;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <h1>🛴 VOI Fleet Dashboard – Norway</h1>
    {buttons_html}
    <div class="timestamp">Last updated: {timestamp}</div>
</body>
</html>
"""

with open("index.html", "w") as f:
    f.write(html)

print("✅ Dashboard written to index.html using live Python data")
