# This script reads the vfc_tests_config.json file and executes tests accordingly
# It will also generate a ... .vfcrun.json file with the results of the run

import os
import json
import glob

import sys

import calendar
import time

import pandas as pd
import numpy as np

import base64
import struct


    # Helper functions

# Read a CSV file outputted by vfc_probe as a Pandas dataframe
def read_probes_csv(filepath, backend):

    results = pd.read_csv(filepath)

    # NOTE The lambda function should probably change depending on if the system
    # uses little or big endian
    results["value"] = results["value"].apply(lambda x: float.fromhex(x))

    results[["test", "variable"]] = results["key"].str.split(':', expand=True)

    del results["key"]
    results.rename(columns = {"value":"values"}, inplace = True)

    results["vfc_backend"] = backend

    return results

def numpy_float_array(x):
    return np.array(x).astype(float)

def get_quantile(array, p):
    return np.quantile(array, p)

################################################################################



    # Open and read the tests config file

try:
    with open("vfc_tests_config.json", "r") as file:
        data = file.read()

except FileNotFoundError as e:
    e.strerror = "This file is required to describe the tests to run and "\
    "generate a Verificarlo run file"
    raise e

config = json.loads(data)



    # Parse CLI arguments

is_git_commit = False
export_raw_values = False

for i in range(1, len(sys.argv)):
    if sys.argv[i] == "--is-git-commit" or sys.argv[i] == "-g":
        is_git_commit = True

    if sys.argv[i] == "--export-raw-values" or sys.argv[i] == "-r":
        export_raw_values = True



    # Set up metadata

# Metadata and filename are initiated as if no commit was associated
metadata = {
    "timestamp": calendar.timegm(time.gmtime()),
    "is_git_commit": is_git_commit,
    "hash": "",
    "author": "",
    "message": ""
}
filename = str(metadata["timestamp"])

if is_git_commit:
    print("Fetching metadata from last commit...")
    from git import Repo

    repo = Repo(".")
    head_commit = repo.head.commit

    metadata["timestamp"] = head_commit.authored_date
    filename = str(head_commit)[0:7]

    metadata["hash"] = str(head_commit)[0:7]
    metadata["author"] = str(head_commit.author) + " <" + head_commit.author.email + ">"
    metadata["message"] = head_commit.message.split("\n")[0]



    # Run the build command

print("Building tests...")
os.system(config["make_command"])



    # Execute all tests and collect results in a Pandas dataframe

data = [] # This is an array of Pandas dataframes for now

# Create tmp folder to export results
os.system("mkdir .vfcruns.tmp")
n_file = 0

for executable in config["executables"]:
    print("Running executable :", executable["executable"], "...")

    parameters = ""
    if "parameters" in executable:
        parameters = executable["parameters"]

    for backend in executable["vfc_backends"]:

        export_backend = "VFC_BACKENDS=\"" + backend["name"] + "\" "
        command = "./" + executable["executable"] + " " + parameters

        repetitions = 1
        if "repetitions" in backend:
            repetitions = backend["repetitions"]

        # Run test repetitions and save results
        for i in range(repetitions):
            file = ".vfcruns.tmp/" + str(n_file) + ".csv"
            export_output = "VFC_PROBES_OUTPUT=\"" + file + "\" "
            os.system(export_output + export_backend + command)


            data.append(read_probes_csv(file, backend["name"]))

            n_file = n_file + 1


# Clean output files
os.system("rm -rf .vfcruns.tmp")

# Combine all separate executions in one dataframe
data = pd.concat(data, sort=False, ignore_index=True)
data = data.groupby(["test", "vfc_backend", "variable"]).values.apply(list).reset_index()



    # Data processing

print("Processing data...")

data["values"] = data["values"].apply(numpy_float_array)

data["mu"] = data["values"].apply(np.average)
data["sigma"] = data["values"].apply(np.std)

# NOTE : What about s when the sample's avg is 0 ? (divison by 0 returns NaN)
data["s10"] = - np.log10(np.absolute( data["sigma"] / data["mu"] ))
data["s2"] = - np.log2(np.absolute( data["sigma"] / data["mu"] ))

data["values"] = data["values"].apply(np.sort)
data["min"] = data["values"].apply(np.min)
data["quantile25"] = data["values"].apply(get_quantile, args=(0.25,))
data["quantile50"] = data["values"].apply(get_quantile, args=(0.5,))
data["quantile75"] = data["values"].apply(get_quantile, args=(0.75,))
data["max"] = data["values"].apply(np.max)



    # Export to HDF5

# Prepare data
data = data.set_index(["test", "variable", "vfc_backend"]).sort_index()
data["timestamp"] = metadata["timestamp"]

# Prepare metadata
metadata = pd.DataFrame.from_dict([metadata])
metadata = metadata.set_index("timestamp")

# NOTE : Exporting to HDF5 requires to install "tables" on the system
if export_raw_values:
    data.to_hdf(filename + ".vfcraw.hd5", key="data")
    metadata.to_hdf(filename + ".vfcraw.hd5", key="metadata")

del data["values"]

data.to_hdf(filename + ".vfcrun.hd5", key="data")
metadata.to_hdf(filename + ".vfcrun.hd5", key="metadata")

print()
print("The results have been successfully written to \"" + filename + ".vfcrun.hd5\".")

if export_raw_values:
    print("A file containing the raw values has also been written to \"" + filename + ".vfcraw.hd5\".")
