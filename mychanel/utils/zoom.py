import requests
from django.conf import settings
import base64

def get_zoom_access_token():
    client_id = settings.ZOOM_CLIENT_ID
    client_secret = settings.ZOOM_CLIENT_SECRET

    auth_str = f"{client_id}:{client_secret}"
    auth_bytes = auth_str.encode('utf-8')
    auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')

    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "account_credentials",
        "account_id": settings.ZOOM_ACCOUNT_ID
    }

    response = requests.post("https://zoom.us/oauth/token", headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("Zoom access token fetch failed", response.text)

import requests
import time

def register_zoom_user(webinar_id, email, first_name, last_name=''):
    token = get_zoom_access_token()
    url = f"https://api.zoom.us/v2/webinars/{webinar_id}/registrants"

    payload = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name or "Attendee"
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("🔥 Zoom API error:", e)
        raise Exception("Zoom registration failed", str(e))

    return response.json().get("join_url")
