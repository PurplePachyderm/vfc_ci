# This script reads the vfc_tests_config.json and executes the tests accordingly
# It will also generate a ....vfcrun.json file with the results of the run

import os
import json

import calendar
import time


# Open and read the tests config file

try:
    with open('vfc_tests_config.json', 'r') as file:
        data = file.read()

except FileNotFoundError as e:
    e.strerror = "This file is required to describe the tests to run and generate a Verificarlo run file"
    raise e

config = json.loads(data)


# Initialize the results object

results = {
    "timestamp": calendar.timegm(time.gmtime()),

        # Hardcoding git values for now
        "is_git_commit": True,
        "commit_data": {
            "hash": "testrun",
            "author": "John Doe <john@doe.com>",
            "message": "This is a fake test commit",
            "description": "This a veeeeery looooong description for the fake commit... Lorem ipsum dolor sit amet..."
        },

        "tests": []
}


# Run the build command
os.system(config["make_command"])


# Execute all tests and fill the results object


# Export the results object as a json file
