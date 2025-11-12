# rks_api_utils.py

from datetime import datetime, timedelta, timezone
from uuid import uuid4
import os
import pandas as pd
from typing import Optional, Dict
import jwt  
import requests 
from dateutil import parser
from dotenv import load_dotenv


def get_service_access_token(service_account_name, token_url) -> str:
    assertion = {
        "iss": service_account_name,
        "sub": service_account_name,
        "aud": token_url,
        "exp": datetime.now().timestamp() + 200,
        "jti": str(uuid4()),
    }

    with open(os.getenv("RKS_PRIVATE_KEY_PATH"), "r") as f:
        private_key = f.read()

    signed_assertion = jwt.encode(payload=assertion, key=private_key, algorithm="RS256")
    token_payload = {
        "scope": "api",
        "grant_type": "client_credentials",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": signed_assertion
    }
    response = requests.post(url=token_url, data=token_payload)
    response.raise_for_status()
    return response.json()["access_token"]

def get_from_api(
    base_url: str,
    service_access_token: str,
    resource_url: str,
    query_params: Optional[Dict[str, str]] = None,
    raise_error: bool = True
) -> requests.Response:
    if query_params is None:
        query_params = {}

    headers = {
        "Authorization": f'Bearer {service_access_token}',
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8"
    }

    url = f'{base_url}/{resource_url}'
    response = requests.get(url=url, params=query_params, headers=headers)

    if raise_error:
        response.raise_for_status()

    return response


def safe_parse_iso(s):
    try:
        return parser.isoparse(s)
    except Exception as e:
        print(f"Skipping invalid timestamp: {s} – {e}")
        return None


def get_all_participants(project_id, access_token):
    """
    Fetches all participants in the given MyDataHelps project.

    Returns:
        list of participant objects.
    """
    url = f"https://mydatahelps.org/api/v1/administration/projects/{project_id}/participants"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch participants: {response.status_code} - {response.text}")

    return response.json().get("participants", [])

def get_surveys(project_id, access_token, participant_id):

    url = f"https://mydatahelps.org/api/v1/administration/projects/{project_id}/participants/{participant_id}/surveyevents"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch surveys for {participant_id}: {response.status_code} - {response.text}")

    return response.json().get("surveyEvents", [])

def get_participant_ids(
    service_access_token: str,
    base_url: str,
    project_id: str,
    page_size: int = 100
):
    """
    Fetch all participantIdentifiers from the project.
    """
    ids = []
    page_number = 0

    while True:
        query_params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "sortBy": "InsertedDate",
            "sortAscending": "true"
        }

        response = get_from_api(
            base_url,
            service_access_token=service_access_token,
            resource_url=f"api/v1/administration/projects/{project_id}/participants",
            query_params=query_params,
            raise_error=True
        )
        data = response.json()
        items = data.get("participants", [])
        if not items:
            break

        ids.extend([p.get("participantIdentifier") for p in items])
        if len(items) < page_size:
            break

        page_number += 1

    return ids

def get_participants_in_segment(service_access_token, base_url, project_id, segment_id, page_size=100):
    """
    Return all participantIdentifiers for a given segment.
    """
    participants = []
    page_number = 0

    headers = {
        "Authorization": f"Bearer {service_access_token}",
        "Accept": "application/json"
    }

    while True:
        params = {
            "segmentID": segment_id,
            "pageSize": page_size,
            "pageNumber": page_number
        }

        url = f"{base_url}/api/v1/administration/projects/{project_id}/participants"
        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        data = r.json()

        items = data.get("participants", [])
        if not items:
            break

        participants.extend([p["participantIdentifier"] for p in items])

        if len(items) < page_size:
            break
        page_number += 1

    return participants
