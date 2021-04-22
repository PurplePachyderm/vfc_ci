# This script reads the vfc_tests_config.json file and executes tests accordingly
# It will also generate a ... .vfcrun.json file with the results of the run

import os
import json

import calendar
import time

# Forcing an older pickle protocol allows backwards compatibility when reading
# HDF5 written in 3.8+ using an older version of Python
import pickle
pickle.HIGHEST_PROTOCOL = 4

import pandas as pd
import numpy as np
import scipy.stats

import sigdigits as sd


################################################################################


    # Helper functions

# Read a CSV file outputted by vfc_probe as a Pandas dataframe
def read_probes_csv(filepath, backend, warnings, execution_data):

    try:
        results = pd.read_csv(filepath)

    except FileNotFoundError:
        print(
            "Warning [vfc_ci]: Probes not found, your code might have crashed " \
            "or you might have forgotten to call vfc_dump_probes"
        )
        warnings.append(execution_data)
        return pd.DataFrame(
            columns = ["test", "variable", "values", "vfc_backend"]
        )

    except Exception:
        print(
            "Warning [vfc_ci]: Your probes could not be read for some unknown " \
            "reason"
        )
        warnings.append(execution_data)
        return pd.DataFrame(
            columns = ["test", "variable", "values", "vfc_backend"]
        )

    if len(results) == 0:
        print(
            "Warning [vfc_ci]: Probes empty, it looks like you have dumped " \
            "them without calling vfc_put_probe"
        )
        warnings.append(execution_data)


    results["value"] = results["value"].apply(lambda x: float.fromhex(x))
    results.rename(columns = {"value":"values"}, inplace = True)

    results["vfc_backend"] = backend

    return results


# Wrapper to sd.significant_digits  (returns result in base 2)
def significant_digits(x):

    # In a pandas DF, "values" actually refers to the array of columns, and
    # not the column named "values"
    values = x.values[3]
    method = sd.Method.General if x.pvalue < 0.05 else sd.Method.CNH

    values = values.reshape(len(values), 1)

    # Since we will be comparing values with themselves, we need to have
    # len(values) % 2 == 0. When it's not verified, we double the last element
    if len(values) % 2 != 0:
        values.append(values[:1])

    s = sd.significant_digits(
        values.reshape(len(values), 1),
        None,
        precision=sd.Precision.Absolute,
        method=method
    )

    return s[0]



################################################################################


    # Main functions


    # Open and read the tests config file

def read_config():
    try:
        with open("vfc_tests_config.json", "r") as file:
            data = file.read()

    except FileNotFoundError as e:
        e.strerror = "Error [vfc_ci]: This file is required to describe the tests "\
        "to run and generate a Verificarlo run file"
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

def run_tests(config):

    # Run the build command
    print("Info [vfc_ci]: Building tests...")
    os.system(config["make_command"])


    # This is an array of Pandas dataframes for now
    data = []


    # Create tmp folder to export results
    os.system("mkdir .vfcruns.tmp")
    n_files = 0


    # This will contain all executables/repetition numbers from which we could
    # not get any data
    warnings = []

    # Tests execution loop
    for executable in config["executables"]:
        print("Info [vfc_ci]: Running executable :", executable["executable"], "...")

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
                file = ".vfcruns.tmp/%s.csv" % str(n_files)
                export_output = "VFC_PROBES_OUTPUT=\"%s\" " % file
                os.system(export_output + export_backend + command)

                # This will only be used if we need to append this exec to the
                # warnings list
                execution_data = {
                    "executable": executable["executable"],
                    "backend": backend["name"],
                    "repetition": i + 1
                }

                data.append(read_probes_csv(
                    file,
                    backend["name"],

                    warnings,
                    execution_data
                ))

                n_files = n_files + 1


    # Clean CSV output files (by deleting the tmp folder)
    os.system("rm -rf .vfcruns.tmp")


    # Combine all separate executions in one dataframe
    data = pd.concat(data, sort=False, ignore_index=True)
    data = data.groupby(["test", "vfc_backend", "variable"])\
    .values.apply(list).reset_index()


    # Make sure we have some data to work on
    assert(len(data) != 0), "Error [vfc_ci]: No data have been generated " \
    "by your tests executions, aborting run without writing results file"

    return data, warnings



    # Display all executions that resulted in a warning
def show_warnings(warnings):
    if len(warnings) > 0:
        print(
            "Warning [vfc_ci]: Some of your runs could not generate any data " \
            "(for instance because your code crashed) and resulted in "
            "warnings. Here is the complete list :"
        )

        for i in range(0, len(warnings)):
            print("- Warning %s:" % i)

            print("  Executable: %s" % warnings[i]["executable"])
            print("  Backend: %s" % warnings[i]["backend"])
            print("  Repetition: %s" % warnings[i]["repetition"])


    # Main function

def run(is_git_commit, export_raw_values):

    # Get config, metadata and data
    print("Info [vfc_ci]: Reading tests config file...")
    config = read_config()

    print("Info [vfc_ci]: Generating run metadata...")
    metadata = generate_metadata(is_git_commit)

    data, warnings = run_tests(config)
    show_warnings(warnings)


    # Data processing
    print("Info [vfc_ci]: Processing data...")

    data["values"] = data["values"].apply(lambda x: np.array(x).astype(float))

    data["mu"] = data["values"].apply(np.average)
    data["sigma"] = data["values"].apply(np.std)
    data["pvalue"] = data["values"].apply(lambda x: scipy.stats.shapiro(x).pvalue)


    # data["s2"] = - np.log2(np.absolute( data["sigma"] / data["mu"] ))
    # data["s10"] = - np.log10(np.absolute( data["sigma"] / data["mu"] ))

    data["s2"] = data.apply(significant_digits, axis=1)
    data["s10"] = data["s2"].apply(lambda x: sd.change_base(x, 10))


    data["values"] = data["values"].apply(np.sort)
    data["min"] = data["values"].apply(np.min)
    data["quantile25"] = data["values"].apply(np.quantile, args=(0.25,))
    data["quantile50"] = data["values"].apply(np.quantile, args=(0.50,))
    data["quantile75"] = data["values"].apply(np.quantile, args=(0.75,))
    data["max"] = data["values"].apply(np.max)
    data["nsamples"] = data["values"].apply(len)


    # Prepare data for export
    data = data.set_index(["test", "variable", "vfc_backend"]).sort_index()
    data["timestamp"] = metadata["timestamp"]

    filename = metadata["hash"] if is_git_commit else str(metadata["timestamp"])


    # Prepare metadata for export
    metadata = pd.DataFrame.from_dict([metadata])
    metadata = metadata.set_index("timestamp")


    # NOTE : Exporting to HDF5 requires to install "tables" on the system

    # Export raw data if needed
    if export_raw_values:
        data.to_hdf(filename + ".vfcraw.hd5", key="data")
        metadata.to_hdf(filename + ".vfcraw.hd5", key="metadata")

    # Export data
    del data["values"]
    data.to_hdf(filename + ".vfcrun.hd5", key="data")
    metadata.to_hdf(filename + ".vfcrun.hd5", key="metadata")


    # Print termination messages
    print(
        "Info [vfc_ci]: The results have been successfully written to %s.vfcrun.hd5." \
         % filename
     )

    if export_raw_values:
        print(
            "Info [vfc_ci]: A file containing the raw values has also been " \
            "created : %s.vfcraw.hd5."
            % filename
        )
