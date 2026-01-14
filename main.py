#!/usr/bin/env python3
import json
import os
import time
from datetime import datetime

import requests
from dotenv import load_dotenv
from escpos.printer import Usb

import config

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

VID = config.VENDOR_ID
PID = config.PRODUCT_ID

ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
TOKEN_URL = "https://www.strava.com/api/v3/oauth/token"

METERS_PER_MILE = 1609.344


def refresh_token() -> dict:
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
        }
    res = requests.post(TOKEN_URL, data=data)
    res.raise_for_status()
    return res.json()


def get_access_token() -> str:
    try:
        with open(".token_cache", "r") as f:
            cached = json.load(f)
            # 5 minute buffer to use token before it expires
            if time.time() < cached["expires_at"] - 300:
                return cached["access_token"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        pass

    data = refresh_token()

    try:
        with open(".token_cache", "w") as f:
            json.dump({
                "access_token": data["access_token"],
                "expires_at": data["expires_at"]
            }, f)
    except OSError as e:
        print(f"Failed to write to token cache: {e}")
    
    return data["access_token"]


def get_newest_activity(access_token: str) -> dict | None:
    headers = { "Authorization": f"Bearer {access_token}" }
    res = requests.get(
        ACTIVITIES_URL, 
        headers=headers, 
        timeout=15
    )
    res.raise_for_status()
    activities = res.json()
    return activities[0] if activities else None


def print_receipt(activity: dict) -> None:
    p = Usb(VID, PID)
    p.set(align="center")
    p.text("\n" * 3)

    p.set(bold=True, double_height=True)
    p.text(f"Strava {activity['type']}\n")
    p.set(bold=False, double_height=False)

    # Date
    date = datetime.strptime(activity["start_date_local"], '%Y-%m-%dT%H:%M:%SZ')
    date_formatted = date.strftime('%b %d, %Y %I:%M %p')

    # Distance
    distance_miles = activity["distance"] / METERS_PER_MILE
    distance_formatted = f"{distance_miles:.2f} mi"

    # Moving Time
    hours, remainder = divmod(activity["moving_time"], 3600)
    minutes, seconds = divmod(remainder, 60)
    moving_time_formatted = f"{hours}:{minutes:02}:{seconds:02}"

    # Pace
    if distance_miles > 0:
        seconds_per_mile = round(activity["moving_time"] / distance_miles)
        pace_minutes, pace_seconds = divmod(seconds_per_mile, 60)
        pace_formatted = f"{pace_minutes}:{pace_seconds:02} /mi"
    else:
        pace_formatted = ""
    
    p.set(align="left")
    p.text("\n")
    p.text(f"Date: {date_formatted}\n")
    if distance_miles > 0:
        p.text(f"Distance: {distance_formatted}\n")
    p.text(f"Moving Time: {moving_time_formatted}\n") 
    if pace_formatted:
        p.text(f"Avg Pace: {pace_formatted}\n")

    p.text("\n" * 3)
    p.cut()


def main() -> None:
    access_token = get_access_token()
    activity = get_newest_activity(access_token)
    if activity:
        print_receipt(activity)    
    else:
        print("No activity to print")


if __name__ == "__main__":
    main()
