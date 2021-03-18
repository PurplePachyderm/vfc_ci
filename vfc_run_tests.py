# This script reads the vfc_tests_config.json and executes the tests accordingly
# It will also generate a ... .vfcrun.json file with the results of the run

import os
import subprocess
import json

import sys
from git import Repo

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


    # Check the "--is-git-commit" argument
    # (and if detected, get last commit's metadata)

# Default value is the current timestamp. If the run is associated with a git commit,
# it will be replaced by the commit's timestamp.
timestamp = calendar.timegm(time.gmtime())

commit_metadata = {}
is_git_commit = False

if len(sys.argv) > 1:
    if sys.argv[1] == "--is-git-commit":
        print("Fetching metadata from last commit...")
        is_git_commit = True

        repo = Repo(".")
        head_commit = repo.head.commit

        timestamp = head_commit.authored_date

        commit_metadata["hash"] = str(head_commit)[0:7]
        commit_metadata["author"] = str(head_commit.author) + " <" + head_commit.author.email + ">"
        commit_metadata["message"] = head_commit.message


    # Initialize the vfcrun object that will be exported

vfcrun = {
    "timestamp": timestamp,

    # Hardcoding git values for now
    "is_git_commit": is_git_commit,
    "commit_metadata": commit_metadata,

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

        export_backend = 'VFC_BACKENDS="' + backend["name"] + '" '
        command = "./" + test["executable"]

        # Run test repetitions and save results
        for i in range(backend["repetitions"]):
            output = subprocess.check_output(export_backend + command, shell=True, encoding="utf-8")

            # val is saved as a string because it's gonna be stored in the run file anyway
            val = output.splitlines()[-1]
            values.append(val)

        # Append the results for this backend to the test
        vfcrun["tests"][-1]["results"].append({
            "vfc_backend": backend["name"],
            "values": values
        })


# Export the results object as a JSON file

if is_git_commit:
    file_name = commit_metadata["hash"] + ".vfcrun.json"

else:
    file_name = str(timestamp) + ".vfcrun.json"

print("\nRun succesful, exporting results in", file_name)

with open(file_name, 'w', encoding='utf8') as f:
    json.dump(vfcrun, f, ensure_ascii=False)
