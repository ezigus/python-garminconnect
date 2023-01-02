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
import time

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
    garmin_data.update({"training_status": full_name})
    garmin_data.update({"date": today.isoformat()})


def get_activity_data():
    # USER STATISTIC SUMMARIES
    # Get activity data for 'YYYY-MM-DD'
    activity_data = api.get_stats(today.isoformat())
    display_json(f"api.get_stats('{today.isoformat()}')", activity_data)
    garmin_data.update({"training_status": activity_data})


def get_HRV():
    # Get Heart Rate Variability (hrv) data
    hrv_data = api.get_hrv_data(today.isoformat())
    display_json(f"api.get_hrv_data({today.isoformat()})", hrv_data)
    garmin_data.update({"training_status": hrv_data})


def get_sleep_data():
    # Get sleep data for 'YYYY-MM-DD'
    sleep_data = api.get_sleep_data(today.isoformat())
    display_json(f"sleep_data ('{today.isoformat()}')", sleep_data)
    garmin_data.update({"training_status": sleep_data})


def get_stress_data():
    stress_data = api.get_stress_data(today.isoformat())
    # Get stress data for 'YYYY-MM-DD'
    display_json(f"stress_data ('{today.isoformat()}')", stress_data)
    garmin_data.update({"training_status": stress_data})


def get_training_status():
    # Get training status data for 'YYYY-MM-DD'
    training_status = api.get_training_status(today.isoformat())
    display_json(f"api.get_training_status('{today.isoformat()}')", training_status)
    garmin_data.update({"training_status": training_status})


def write_garmin_data():
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

        if check_date:
            print(f"date {today.isoformat()} found")
            return

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

    print(garmin_data)

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

        #         elif i == "6":
        #             # Get body composition data for multiple days 'YYYY-MM-DD' (to be compatible with garminconnect-ha)
        #             display_json(
        #                 f"api.get_body_composition('{startdate.isoformat()}', '{today.isoformat()}')",
        #                 api.get_body_composition(startdate.isoformat(), today.isoformat()),
        #             )
        #         elif i == "7":
        #             # Get stats and body composition data for 'YYYY-MM-DD'
        #             display_json(
        #                 f"api.get_stats_and_body('{today.isoformat()}')",
        #                 api.get_stats_and_body(today.isoformat()),
        #             )

        #         # USER STATISTICS LOGGED
        #         elif i == "8":
        #             # Get steps data for 'YYYY-MM-DD'
        #             display_json(
        #                 f"api.get_steps_data('{today.isoformat()}')",
        #                 api.get_steps_data(today.isoformat()),
        #             )
        #         elif i == "9":
        #             # Get heart rate data for 'YYYY-MM-DD'
        #             display_json(
        #                 f"api.get_heart_rates('{today.isoformat()}')",
        #                 api.get_heart_rates(today.isoformat()),
        #             )
        #         elif i == "a":
        #             # Get resting heart rate data for 'YYYY-MM-DD'
        #             display_json(
        #                 f"api.get_rhr_day('{today.isoformat()}')",
        #                 api.get_rhr_day(today.isoformat()),
        #             )
        #         elif i == "b":
        #             # Get hydration data 'YYYY-MM-DD'
        #             display_json(
        #                 f"api.get_hydration_data('{today.isoformat()}')",
        #                 api.get_hydration_data(today.isoformat()),
        #             )
        #         elif i == "e":
        #             # Get respiration data for 'YYYY-MM-DD'
        #             display_json(
        #                 f"api.get_respiration_data('{today.isoformat()}')",
        #                 api.get_respiration_data(today.isoformat()),
        #             )
        #         elif i == "f":
        #             # Get SpO2 data for 'YYYY-MM-DD'
        #             display_json(
        #                 f"api.get_spo2_data('{today.isoformat()}')",
        #                 api.get_spo2_data(today.isoformat()),
        #             )
        #         elif i == "h":
        #             # Get personal record for user
        #             display_json("api.get_personal_record()", api.get_personal_record())
        #         elif i == "i":
        #             # Get earned badges for user
        #             display_json("api.get_earned_badges()", api.get_earned_badges())
        #         elif i == "j":
        #             # Get adhoc challenges data from start and limit
        #             display_json(
        #                 f"api.get_adhoc_challenges({start},{limit})",
        #                 api.get_adhoc_challenges(start, limit),
        #             )  # 1=start, 100=limit
        #         elif i == "k":
        #             # Get available badge challenges data from start and limit
        #             display_json(
        #                 f"api.get_available_badge_challenges({start_badge}, {limit})",
        #                 api.get_available_badge_challenges(start_badge, limit),
        #             )  # 1=start, 100=limit
        #         elif i == "l":
        #             # Get badge challenges data from start and limit
        #             display_json(
        #                 f"api.get_badge_challenges({start_badge}, {limit})",
        #                 api.get_badge_challenges(start_badge, limit),
        #             )  # 1=start, 100=limit
        #         elif i == "m":
        #             # Get non completed badge challenges data from start and limit
        #             display_json(
        #                 f"api.get_non_completed_badge_challenges({start_badge}, {limit})",
        #                 api.get_non_completed_badge_challenges(start_badge, limit),
        #             )  # 1=start, 100=limit

        #         # ACTIVITIES
        #         elif i == "n":
        #             # Get activities data from start and limit
        #             display_json(
        #                 f"api.get_activities({start}, {limit})",
        #                 api.get_activities(start, limit),
        #             )  # 0=start, 1=limit
        #         elif i == "o":
        #             # Get last activity
        #             display_json("api.get_last_activity()", api.get_last_activity())
        #         elif i == "p":
        #             # Get activities data from startdate 'YYYY-MM-DD' to enddate 'YYYY-MM-DD', with (optional) activitytype
        #             # Possible values are: cycling, running, swimming, multi_sport, fitness_equipment, hiking, walking, other
        #             activities = api.get_activities_by_date(
        #                 startdate.isoformat(), today.isoformat(), activitytype
        #             )

        #             # Download activities
        #             for activity in activities:

        #                 activity_id = activity["activityId"]
        #                 display_text(activity)

        #                 print(
        #                     f"api.download_activity({activity_id}, dl_fmt=api.ActivityDownloadFormat.GPX)"
        #                 )
        #                 gpx_data = api.download_activity(
        #                     activity_id, dl_fmt=api.ActivityDownloadFormat.GPX
        #                 )
        #                 output_file = f"./{str(activity_id)}.gpx"
        #                 with open(output_file, "wb") as fb:
        #                     fb.write(gpx_data)
        #                 print(f"Activity data downloaded to file {output_file}")

        #                 print(
        #                     f"api.download_activity({activity_id}, dl_fmt=api.ActivityDownloadFormat.TCX)"
        #                 )
        #                 tcx_data = api.download_activity(
        #                     activity_id, dl_fmt=api.ActivityDownloadFormat.TCX
        #                 )
        #                 output_file = f"./{str(activity_id)}.tcx"
        #                 with open(output_file, "wb") as fb:
        #                     fb.write(tcx_data)
        #                 print(f"Activity data downloaded to file {output_file}")

        #                 print(
        #                     f"api.download_activity({activity_id}, dl_fmt=api.ActivityDownloadFormat.ORIGINAL)"
        #                 )
        #                 zip_data = api.download_activity(
        #                     activity_id, dl_fmt=api.ActivityDownloadFormat.ORIGINAL
        #                 )
        #                 output_file = f"./{str(activity_id)}.zip"
        #                 with open(output_file, "wb") as fb:
        #                     fb.write(zip_data)
        #                 print(f"Activity data downloaded to file {output_file}")

        #                 print(
        #                     f"api.download_activity({activity_id}, dl_fmt=api.ActivityDownloadFormat.CSV)"
        #                 )
        #                 csv_data = api.download_activity(
        #                     activity_id, dl_fmt=api.ActivityDownloadFormat.CSV
        #                 )
        #                 output_file = f"./{str(activity_id)}.csv"
        #                 with open(output_file, "wb") as fb:
        #                     fb.write(csv_data)
        #                 print(f"Activity data downloaded to file {output_file}")

        #         elif i == "s":
        #             # Upload activity from file
        #             display_json(
        #                 f"api.upload_activity({activityfile})",
        #                 api.upload_activity(activityfile),
        #             )

        #         # DEVICES
        #         elif i == "t":
        #             # Get Garmin devices
        #             devices = api.get_devices()
        #             display_json("api.get_devices()", devices)

        #             # Get device last used
        #             device_last_used = api.get_device_last_used()
        #             display_json("api.get_device_last_used()", device_last_used)

        #             # Get settings per device
        #             for device in devices:
        #                 device_id = device["deviceId"]
        #                 display_json(
        #                     f"api.get_device_settings({device_id})",
        #                     api.get_device_settings(device_id),
        #                 )

        #         # GOALS
        #         elif i == "u":
        #             # Get active goals
        #             goals = api.get_goals("active")
        #             display_json('api.get_goals("active")', goals)

        #         elif i == "v":
        #             # Get future goals
        #             goals = api.get_goals("future")
        #             display_json('api.get_goals("future")', goals)

        #         elif i == "w":
        #             # Get past goals
        #             goals = api.get_goals("past")
        #             display_json('api.get_goals("past")', goals)

        #         # Gear
        #         elif i == "G":
        #             last_used_device = api.get_device_last_used()
        #             display_json(f"api.get_device_last_used()", last_used_device)
        #             userProfileNumber = last_used_device["userProfileNumber"]
        #             gear = api.get_gear(userProfileNumber)
        #             display_json(f"api.get_gear()", gear)
        #             display_json(
        #                 f"api.get_gear_defaults()", api.get_gear_defaults(userProfileNumber)
        #             )
        #             display_json(f"api.get()", api.get_activity_types())
        #             for gear in gear:
        #                 uuid = gear["uuid"]
        #                 name = gear["displayName"]
        #                 display_json(
        #                     f"api.get_gear_stats({uuid}) / {name}", api.get_gear_stats(uuid)
        #                 )

        #         elif i == "Z":
        #             # Logout Garmin Connect portal
        #             display_json("api.logout()", api.logout())
        #             api = None

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
