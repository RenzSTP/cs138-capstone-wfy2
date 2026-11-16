import requests
import pandas as pd
from getpass import getpass

API_KEY = getpass("OpenAQ API key: ")
BASE = "https://api.openaq.org/v3"
LOCATION_ID = 4526988

# Manila time (UTC+08:00)
START = "2026-06-01T00:00:00+08:00"
END = "2026-07-01T00:00:00+08:00"

session = requests.Session()
session.headers.update({"X-API-Key": API_KEY})

def fetch(path, params=None):
    response = session.get(
        f"{BASE}/{path}", params=params, timeout=60
    )
    response.raise_for_status()
    return response.json()["results"]

# Find the PM2.5 sensors belonging to this location.
sensors = fetch(f"locations/{LOCATION_ID}/sensors")
pm25_sensors = [
    sensor for sensor in sensors
    if sensor["parameter"]["name"] == "pm25"
]

if not pm25_sensors:
    raise RuntimeError("No PM2.5 sensor found for this location.")

rows = []

for sensor in pm25_sensors:
    page = 1

    while True:
        measurements = fetch(
            f"sensors/{sensor['id']}/days",
            params={
                "date_from": "2026-06-01",
                "date_to": "2026-06-30",
                "limit": 1000,
                "page": page,
            },
        )

        for m in measurements:
            rows.append({
                "sensor_id": sensor["id"],
                "datetime_from": m["period"]["datetimeFrom"]["local"],
                "datetime_to": m["period"]["datetimeTo"]["local"],
                "pm25": m["value"],
                "units": m["parameter"]["units"],
                "hours_observed": (m.get("coverage") or {}).get("observedCount"),
                "coverage_percent": (m.get("coverage") or {}).get("percentCoverage"),
            })

        if len(measurements) < 1000:
            break

        page += 1

df = pd.DataFrame(rows)

if df.empty:
    print("No measurements returned for this date range.")
else:
    # OpenAQ timestamps mark the end of the measurement period.
    timestamps = pd.to_datetime(df["datetime_to"], utc=True)
    df = df[
        (timestamps > pd.Timestamp(START))
        & (timestamps <= pd.Timestamp(END))
    ].sort_values(["datetime_to", "sensor_id"])

    filename = "openaq_4526988_june_2026_daily_pm25.csv"    
    df.to_csv(filename, index=False)
    print(f"Saved {len(df)} measurements to {filename}")
    print(df.head())