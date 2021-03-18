# Look for and read all the run files in the current directory (ending with
# .vfcrun.json). It will then generate a "report.html" file.

import os
import json

import numpy as np
import pandas as pd

from bokeh.plotting import figure, show
from bokeh.resources import INLINE
from bokeh.embed import components

from jinja2 import Environment, FileSystemLoader


    # Look for all run files in current directory and read them

print("Looking for run files...")

run_files = [ f for f in os.listdir(".") if f.endswith(".vfcrun.json") ]

runs = []
for f in run_files:
    with open(f, "r") as file:
        runs.append(json.loads(file.read()))


    # Organize the data by results

print("Re-arranging data...")

# Convert dictionary to Pandas dataframe for easier manipulation
runs = pd.DataFrame.from_dict(runs)

# Unroll by tests
runs = runs.explode("tests")
runs = pd.concat([runs.drop(["tests"], axis=1), runs["tests"].apply(pd.Series)], axis=1)

# Unroll by backend results
runs = runs.explode("results")
runs = pd.concat([runs.drop(["results"], axis=1), runs["results"].apply(pd.Series)], axis=1)

runs.rename(columns = {'name':'test'}, inplace = True)
runs = runs.reset_index(drop=True)


# At this point, each dataframe row represents a run for one test/backend combination,
# and has the following columns :
# timestamp, is_git_commit, commit_metadata, test, vfc_backend, values


    # Actual data processing (compute average, standard deviation, significant digits)

print("Processing data...")

def numpy_float_array(x):
    return np.array(x).astype(float)

runs["values"] = runs["values"].apply(numpy_float_array)

runs["mu"] = runs["values"].apply(np.average)
runs["sigma"] = runs["values"].apply(np.std)
runs["s10"] = - np.log10(np.absolute( runs["sigma"] / runs["mu"] ))
runs["s2"] = - np.log2(np.absolute( runs["sigma"] / runs["mu"] ))

# NOTE : What about s when the sample's avg is 0 ? (divison by 0 returns NaN)


    # Generate the Bokeh plots

# Group the runs by test then backend to get a tree-like structure

print("Base dataframe:")
print(runs)


print("Groupby:")
runs = runs.groupby("test")
for key, item in runs:
    print(key)
    print(runs.get_group(key), "\n\n")
    # TODO groupby vfc_backend
