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

################################################################################


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

    # Main functions


    # Open and read the tests config file

def read_config():
    try:
        with open("vfc_tests_config.json", "r") as file:
            data = file.read()

    except FileNotFoundError as e:
        e.strerror = "This file is required to describe the tests to run and "\
        "generate a Verificarlo run file"
        raise e

    return json.loads(data)



    # Set up metadata

def generate_metadata(is_git_commit):

    # Metadata and filename are initiated as if no commit was associated
    metadata = {
        "timestamp": calendar.timegm(time.gmtime()),
        "is_git_commit": is_git_commit,
        "hash": "",
        "author": "",
        "message": ""
    }


    if is_git_commit:
        print("Fetching metadata from last commit...")
        from git import Repo

        repo = Repo(".")
        head_commit = repo.head.commit

        metadata["timestamp"] = head_commit.authored_date

        metadata["hash"] = str(head_commit)[0:7]
        metadata["author"] = "%s <%s>" \
        % (str(head_commit.author), head_commit.author.email)
        metadata["message"] = head_commit.message.split("\n")[0]

    return metadata



    # Execute tests and collect results in a Pandas dataframe (+ dataprocessing)

def generate_data(config):

    # Run the build command
    print("Building tests...")
    os.system(config["make_command"])


    # This is an array of Pandas dataframes for now
    data = []


    # Create tmp folder to export results
    os.system("mkdir .vfcruns.tmp")
    n_file = 0


    # Tests execution loop
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
                file = ".vfcruns.tmp/%s.csv" % str(n_file)
                export_output = "VFC_PROBES_OUTPUT=\"%s\" " % file
                os.system(export_output + export_backend + command)


                data.append(read_probes_csv(file, backend["name"]))

                n_file = n_file + 1


    # Clean CSV output files (by deleting the tmp folder)
    os.system("rm -rf .vfcruns.tmp")


    # Combine all separate executions in one dataframe
    data = pd.concat(data, sort=False, ignore_index=True)
    data = data.groupby(["test", "vfc_backend", "variable"])\
    .values.apply(list).reset_index()


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
    data["nruns"] = data["values"].apply(len)

    return data



    # Main function

def run(is_git_commit, export_raw_values):

    # Get config, metadata and data
    config = read_config()
    metadata = generate_metadata(is_git_commit)
    data = generate_data(config)

    # Prepare data
    data = data.set_index(["test", "variable", "vfc_backend"]).sort_index()
    data["timestamp"] = metadata["timestamp"]

    filename = metadata["hash"] if is_git_commit else str(metadata["timestamp"])

    # Prepare metadata
    metadata = pd.DataFrame.from_dict([metadata])
    metadata = metadata.set_index("timestamp")


    # Export metadata if needed
    # NOTE : Exporting to HDF5 requires to install "tables" on the system
    if export_raw_values:
        data.to_hdf(filename + ".vfcraw.hd5", key="data")
        metadata.to_hdf(filename + ".vfcraw.hd5", key="metadata")


    # Export data
    del data["values"]
    data.to_hdf(filename + ".vfcrun.hd5", key="data")
    metadata.to_hdf(filename + ".vfcrun.hd5", key="metadata")


    # Print termination messages
    print()
    print(
        "The results have been successfully written to \"%s.vfcrun.hd5\"." \
         % filename
     )

    if export_raw_values:
        print(
            "A file containing the raw values has also been written to \"%s.vfcraw.hd5\"." \
            % filename
        )
