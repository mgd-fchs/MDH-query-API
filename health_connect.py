from datetime import datetime, time, timezone, timedelta
import requests
import json
from collections import defaultdict
from api_utils import *


def fetch_measurements(service_access_token, project_id, ids, base_url, data_specs):

    measurement_map = {
        "active_calories": "active-calories-burned",
        "active_calories_daily": "active-calories-burned-daily",
        "blood_glucose": "blood-glucose",
        "blood_pressure_sys": "blood-pressure-systolic",
        "blood_pressure_dia": "blood-pressure-diastolic",
        "body_temp": "body-temperature",
        "distance": "distance",
        "distance_daily": "distance-daily",
        "exercise_segments": "exercise-segments",
        "exercise_lat": "exercise-route-latitude",
        "exercise_lon": "exercise-route-longitude",
        "exercise_alt": "exercise-route-altitude",
        "exercise_hacc": "exercise-route-horizontalAccuracy",
        "exercise_vacc": "exercise-route-verticalAccuracy",
        "exercise_laps": "exercise-laps",
        "exercise_time": None,
        "heart_rate": "heart-rate",
        "heart_rate_min": "heart-rate-daily-minimum",
        "heart_rate_max": "heart-rate-daily-maximum",
        "hrv": None,
        "oxygen_saturation": "oxygen-saturation",
        "respiratory_rate": "respiratory-rate",
        "resting_hr": "resting-heart-rate",
        "sleep": "sleep",
        "steps": "steps",
        "steps_daily": "steps-daily",
        "steps_hourly": "steps-hourly",
        "steps_half_hourly": "steps-half-hourly",
        "total_calories": "total-calories-burned",
        "total_calories_daily": "total-calories-burned-daily",
        "vo2_max": "vo2-max",
        "weight": "weight"
    }

    headers = {
        "Authorization": f"Bearer {service_access_token}",
        "Accept": "application/json"
    }

    url = f"{base_url}/api/v2/administration/projects/{project_id}/devicedatapoints"
    
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
            if meas not in measurement_map:
                print(f"Skipping {meas}: not in Health Connect map")
                continue

            params = {
                "namespace": "HealthConnect",
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

    url = f"{base_url}/api/v2/administration/projects/{project_id}/devicedatapoints/alldatatypes"

    try:
        r = requests.get(url, headers=headers)
        print("All data types:", r)
        r.raise_for_status()

        resp_json = r.json()

        # Filter to only AppleHealth entries before printing
        HC_only = [
            item for item in resp_json
            if item.get("namespace") == "HealthConnect"
        ]

        HC_only = json.dumps(HC_only, indent=2)

    except requests.HTTPError as e:
        print(f"Error accessing data types: {e}")
        return

    return HC_only