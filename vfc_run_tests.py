# This script reads the vfc_tests_config.json and executes the tests accordingly
# It will also generate a ....vfcrun.json file with the results of the run

import os
import subprocess
import json

import calendar
import time


# Open and read the tests config file

try:
    with open("vfc_tests_config.json", "r") as file:
        data = file.read()

except FileNotFoundError as e:
    e.strerror = "This file is required to describe the tests to run and generate a Verificarlo run file"
    raise e

config = json.loads(data)


# Initialize the vfcrun object that will be exported

vfcrun = {
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

print("Building tests...")
os.system(config["make_command"])


# Execute all tests and fill the results object

for test in config["tests"]:
    print("Running test :", test["name"])
    vfcrun["tests"].append({
        "name": test["name"],
        "results": []
    })

    for backend in test["vfc_backends"]:
        values = []
        export_backend = 'export VFC_BACKENDS="' + backend + '"'
        os.system(export_backend)

        command = "./" + test["executable"]

        # Run test repetitions and save results
        for i in range(test["repetitions"]):
            output = subprocess.run(command, stdout=subprocess.PIPE).stdout.decode('utf-8')
            # val is saved as a string because it's gonna be stored in the run file anyway
            val = output.splitlines()[-1]
            values.append(val)

        # Append the results for this backend to the test
        vfcrun["tests"][-1]["results"].append({
            "vfc_backend": backend,
            "values": values
        })


print(vfcrun)

# Export the results object as a json file
