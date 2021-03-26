# Look for and read all the run files in the current directory (ending with
# .vfcrun.hd5), and lanch a Bokeh server for the visualization of this data.


import os
import json
import datetime

import pandas as pd

from bokeh.plotting import figure, show, curdoc
from bokeh.resources import INLINE
from bokeh.embed import components

from jinja2 import Environment, FileSystemLoader


        # Helper functions

# From a timestamp, return the associated metadata as a Pandas serie
def get_metadata(metadata, timestamp):
    return metadata.loc[timestamp]

# From an array of timestamps, return an array of hashes/dates that can
# be used as the x serie of a bar/box plot
def gen_x_series(metadata, timestamps):
    x = []
    for i in range(0, len(timestamps)):
        row_metadata = get_metadata(metadata, timestamps[i])

        if row_metadata["is_git_commit"]:
            x.append(row_metadata["hash"])

        else:
            x.append(datetime.datetime.fromtimestamp(timestamps[i]).isoformat())

    return x


################################################################################


    # Read vfcrun files and generate data/metadata

run_files = [ f for f in os.listdir(".") if f.endswith(".vfcrun.hd5") ]

if len(run_files) == 0:
    print("Could not find any vfcrun files in the directory. Exiting script.")
    exit(1)

# These are arrays of Pandas dataframes for now
metadata = []
data = []

for f in run_files:
    metadata.append(pd.read_hdf(f, "metadata"))
    data.append(pd.read_hdf(f, "data"))

metadata = pd.concat(metadata).sort_index()
data = pd.concat(data).sort_index()

data = data.sort_values("timestamp").sort_index()
data = data.groupby(["test", "variable", "vfc_backend"]).agg(lambda x: list(x))

print(data)



################################################################################


    # WIP Setup Bokeh server

curdoc().title = "Verificarlo Report"

# Plots setup

boxplot = figure(
    name="boxplot", title="Variable repartition over runs",
    plot_width=800, plot_height=300
)
curdoc().add_root(boxplot)

sigma_plot = figure(
    name="sigma_plot", title="Standard deviation σ over runs",
    plot_width=800, plot_height=300
)
curdoc().add_root(sigma_plot)

s_plot = figure(
    name="s_plot", title="Significant digits s over runs",
    plot_width=800, plot_height=300
)
curdoc().add_root(s_plot)


# Widgets setup

select_test = Select(
    name="select_test", title="Test :",
    value="", options=["foo", "bar", "baz", "quux"]
)

select_var = Select(
    name="select_var", title="Variable :",
    value="", options=["foo", "bar", "baz", "quux"]
)

select_backend = Select(
    name="select_backend", title="Verificarlo backend :",
    value="", options=["foo", "bar", "baz", "quux"]
)
