#!/usr/bin/env python3
"""
pip3 install cloudscraper requests readchar pwinput

export EMAIL=<your garmin email>
export PASSWORD=<your garmin password>

"""
import datetime
import json
import logging
import os
import sys


# import pandas as pd

import requests
import pwinput
import readchar

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)

# Configure debug logging
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables if defined
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
api = None

# Example selections and settings
today = datetime.date.today() - datetime.timedelta(days=1)
startdate = today - datetime.timedelta(days=7)  # Select past week
start = 0
limit = 100
start_badge = 1  # Badge related calls calls start counting at 1
activitytype = ""  # Possible values are: cycling, running, swimming, multi_sport, fitness_equipment, hiking, walking, other
activityfile = "MY_ACTIVITY.fit"  # Supported file types are: .fit .gpx .tcx

garmin_data = {}


def get_full_name():
    full_name = api.get_full_name()
    display_json("api.get_full_name()", full_name)
    garmin_data.update({"name": full_name})
    garmin_data.update({"date": today.isoformat()})


def get_activity_data():
    # USER STATISTIC SUMMARIES
    # Get activity data for 'YYYY-MM-DD'
    activity_data = api.get_stats(today.isoformat())
    display_json(f"api.get_stats('{today.isoformat()}')", activity_data)
    garmin_data.update({"Activity": activity_data})


def get_HRV():
    # Get Heart Rate Variability (hrv) data
    hrv_data = api.get_hrv_data(today.isoformat())
    display_json(f"api.get_hrv_data({today.isoformat()})", hrv_data)
    garmin_data.update({"HRV": hrv_data})


def get_sleep_data():
    # Get sleep data for 'YYYY-MM-DD'
    sleep_data = api.get_sleep_data(today.isoformat())
    display_json(f"sleep_data ('{today.isoformat()}')", sleep_data)
    garmin_data.update({"Sleep": sleep_data})


def get_stress_data():
    stress_data = api.get_stress_data(today.isoformat())
    # Get stress data for 'YYYY-MM-DD'
    display_json(f"stress_data ('{today.isoformat()}')", stress_data)
    garmin_data.update({"Stress": stress_data})


def get_training_status():
    # Get training status data for 'YYYY-MM-DD'
    training_status = api.get_training_status(today.isoformat())
    display_json(f"api.get_training_status('{today.isoformat()}')", training_status)
    garmin_data.update({"training_status": training_status})


def display_garmin_data():
    print(garmin_data)


def write_garmin_data():

    if check_garmin_date() == True:
        print(f"Data saved for {today.isoformat()} already")
        return

    # read the original garmin.jso file in, then append any new data retrieved
    # write out to garmin.json file the data retrieved from garmin connect
    with open(
        "/home/ezigus/code/garmin/python-garminconnect/garmin.json", "r+"
    ) as file:
        input_data = json.load(file)

        # but only write the data if the data was not already retrieved
        # checking to see if the data received is already in the garmin.json file
        # check_date = any(
        #     d["date"] == today.isoformat() for d in input_data["garmin_data"]
        # )

        # if check_date:
        #     print(f"date {today.isoformat()} found")
        #     return

        display_text(garmin_data)

        input_data["garmin_data"].append(garmin_data)
        file.seek(0)
        json.dump(input_data, file, indent=4)


def check_garmin_date() -> bool:

    with open("/home/ezigus/code/garmin/python-garminconnect/garmin.json", "r") as file:
        input_data = json.load(file)

        # but only write the data if the data was not already retrieved
        # checking to see if the data received is already in the garmin.json file
        check_date = any(
            d["date"] == today.isoformat() for d in input_data["garmin_data"]
        )
        return check_date


def get_all():

    if check_garmin_date() == True:
        print(f"Data already loaded for {today.isoformat()}")
        return

    get_full_name()
    get_activity_data()
    get_training_status()
    get_HRV()
    get_stress_data()
    get_sleep_data()

    write_garmin_data()


menu_options = {
    "a": (f"Get all z data {today.isoformat()}'", get_all),
    "1": ("Get full name", get_full_name),
    "2": (f"Get activity data for '{today.isoformat()}'", get_activity_data),
    "3": (
        f"Get training status data for '{today.isoformat()}'",
        get_training_status,
    ),
    "4": (f"Get sleep data for '{today.isoformat()}'", get_sleep_data),
    "5": (f"Get stress data for '{today.isoformat()}'", get_stress_data),
    "6": (
        f"Get Heart Rate Variability data (HRV) for '{today.isoformat()}'",
        get_HRV,
    ),
    "d": (f"Display Garmin Data", display_garmin_data),
    "w": (f"Write Garmin Data {today.isoformat()}", write_garmin_data),
    "q": ("Exit", sys.exit),
}


def display_json(api_call, output):
    """Format API output for better readability."""

    dashed = "-" * 20
    header = f"{dashed} {api_call} {dashed}"
    footer = "-" * len(header)

    print(header)
    print(json.dumps(output, indent=4))
    print(footer)


def display_text(output):
    """Format API output for better readability."""

    dashed = "-" * 60
    header = f"{dashed}"
    footer = "-" * len(header)

    print(header)
    print(json.dumps(output, indent=4))
    print(footer)


def get_credentials():
    """Get user credentials."""
    email = input("Login e-mail: ")
    password = pwinput.pwinput(prompt="Password: ")

    return email, password


def init_api(email, password):
    """Initialize Garmin API with your credentials."""

    try:
        ## Try to load the previous session
        with open("session.json") as f:
            saved_session = json.load(f)

            print(
                "Login to Garmin Connect using session loaded from 'session.json'...\n"
            )

            # Use the loaded session for initializing the API (without need for credentials)
            api = Garmin(session_data=saved_session)

            # Login using the
            api.login()

    except (FileNotFoundError, GarminConnectAuthenticationError):
        # Login to Garmin Connect portal with credentials since session is invalid or not present.
        print(
            "Session file not present or turned invalid, login with your Garmin Connect credentials.\n"
            "NOTE: Credentials will not be stored, the session cookies will be stored in 'session.json' for future use.\n"
        )
        try:
            # Ask for credentials if not set as environment variables
            if not email or not password:
                email, password = get_credentials()

            api = Garmin(email, password)
            api.login()

            # Save session dictionary to json file for future use
            with open("session.json", "w", encoding="utf-8") as f:
                json.dump(api.session_data, f, ensure_ascii=False, indent=4)
        except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
            requests.exceptions.HTTPError,
        ) as err:
            logger.error("Error occurred during Garmin Connect communication: %s", err)
            return None

    return api


def print_menu():
    """Print examples menu."""
    for key in menu_options.keys():
        print(f"{key} -- {menu_options[key][0]}")
    print("Make your selection: ", end="", flush=True)


def switch(api, i):
    """Run selected API call."""

    # Exit example program
    # if i == "q":
    #     print("Bye!")
    #     sys.exit()

    # Skip requests if login failed
    if api:
        try:
            if menu_options[i]:
                print(f"\n\nExecuting: {menu_options[i][1].__name__}\n")
                menu_options[i][1]()
            else:
                print("Invalid selection\n")

        except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
            requests.exceptions.HTTPError,
        ) as err:
            logger.error("Error occurred: %s", err)
        except KeyError:
            # Invalid menu option choosen
            pass
    else:
        print("Could not login to Garmin Connect, try again later.")


# Main program loop
while True:
    # Display header and login
    print("\n*** Garmin Connect API Demo by cyberjunky ***\n")

    # Init API
    if not api:
        api = init_api(email, password)

    # Display menu
    print_menu()
    option = readchar.readkey()
    switch(api, option)
