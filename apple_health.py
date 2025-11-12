from datetime import datetime, timedelta, time, timezone
import pytz 
import requests
from collections import defaultdict
import pandas as pd
import json


def fetch_measurements(service_access_token, project_id, ids, base_url, data_specs):

    measurement_map = {
        "active_calories": "TotalEnergyBurned",
        "active_calories_daily": "TotalEnergyBurned",  # no daily variant
        "blood_glucose": "BloodGlucose",
        "blood_pressure_sys": None,  # not available in current list
        "blood_pressure_dia": None,  # not available in current list
        "body_temp": "Temperature",
        "distance": "DistanceWalkingRunning",
        "distance_daily": "TotalDistance",
        "exercise_segments": "WorkoutEvent",
        "exercise_lat": "WorkoutEvent",
        "exercise_lon": "WorkoutEvent",
        "exercise_alt": "WorkoutEvent",
        "exercise_hacc": "WorkoutEvent",
        "exercise_vacc": "WorkoutEvent",
        "exercise_laps": "WorkoutEvent",
        "exercise_time": "AppleExerciseTime",
        "heart_rate": "HeartRate",
        "heart_rate_min": None,  # no matching AppleHealth type
        "heart_rate_max": None,  # no matching AppleHealth type
        "hrv": "HeartRateVariability",
        "oxygen_saturation": None,  # not enabled
        "respiratory_rate": "RespiratoryRate",
        "resting_hr": "RestingHeartRate",
        "sleep": "SleepAnalysisInterval",
        "steps": "Steps",
        "steps_daily": "DailySteps",
        "steps_hourly": "HourlySteps",
        "steps_half_hourly": "HalfHourSteps",
        "total_calories": "TotalEnergyBurned",
        "total_calories_daily": "TotalEnergyBurned",
        "vo2_max": None,  # not enabled
        "weight": None  # not enabled
    }

    headers = {
        "Authorization": f"Bearer {service_access_token}",
        "Accept": "application/json"
    }

    url = f"{base_url}/api/v1/administration/projects/{project_id}/devicedatapoints/"

    # --- Build observedAfter / observedBefore ---
    observed_after, observed_before = None, None
    if data_specs.get("dates"):
        if len(data_specs["dates"]) >= 1 and data_specs["dates"][0]:
            start_date = data_specs["dates"][0]
            observed_after = f"{start_date}T00:00:00Z"
        if len(data_specs["dates"]) >= 2 and data_specs["dates"][1]:
            end_date = data_specs["dates"][1]
            observed_before = f"{end_date}T23:59:59Z"

    results = {}

    for pid in ids:
        results[pid] = {}

        for meas in data_specs["measurements"]:
            params = {
                "namespace": "AppleHealth",
                "type": measurement_map[meas],
                "participantIdentifier": pid
            }

            if observed_after:
                params["observedAfter"] = observed_after
            if observed_before:
                params["observedBefore"] = observed_before

            try:
                r = requests.get(url, headers=headers, params=params)
                r.raise_for_status()
                dps = r.json().get("deviceDataPoints", [])
            except requests.HTTPError as e:
                print(f"Skipping {pid} {meas}: {e}")
                continue

            if not dps:
                continue

            df = pd.DataFrame(dps)
            df["participantID"] = pid
            df["measurement"] = meas
            results[pid][meas] = df

    return results

def get_all_datatypes(service_access_token, project_id, base_url):
    import requests, json

    headers = {
        "Authorization": f"Bearer {service_access_token}",
        "Accept": "application/json"
    }

    url = f"{base_url}/api/v1/administration/projects/{project_id}/devicedatapoints/alldatatypes"

    try:
        r = requests.get(url, headers=headers)
        print("All data types:", r)
        r.raise_for_status()

        resp_json = r.json()

        # Filter to only AppleHealth entries before printing
        apple_health_only = [
            item for item in resp_json
            if item.get("namespace") == "AppleHealth" and item.get("enabled") == True
        ]

        apple_health_only = json.dumps(apple_health_only, indent=2)

    except requests.HTTPError as e:
        print(f"Error accessing data types: {e}")
        return

    return apple_health_only

