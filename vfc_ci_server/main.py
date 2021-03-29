# Look for and read all the run files in the current directory (ending with
# .vfcrun.hd5), and lanch a Bokeh server for the visualization of this data.


import os
import json
import datetime

import pandas as pd

from bokeh.plotting import figure, show, curdoc
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.models import Select, ColumnDataSource, Panel, Tabs

from jinja2 import Environment, FileSystemLoader


        # Helper functions

# From a timestamp, return the associated metadata as a Pandas serie
def get_metadata(timestamp):
    return metadata.loc[timestamp]

# From an array of timestamps, return an array of hashes/dates that can
# be used as the x serie of a bar/box plot
def gen_x_series(timestamps):
    x = []
    for i in range(0, len(timestamps)):
        row_metadata = get_metadata(timestamps[i])

        if row_metadata["is_git_commit"]:
            x.append(row_metadata["hash"])

        else:
            x.append(datetime.datetime.fromtimestamp(timestamps[i]).isoformat())

    return x

# Update plots based on current_test/var/backend combination
def update_plots():

    line = data.loc[current_test, current_var, current_backend]
    x = gen_x_series(line["timestamp"])

    # Update x_ranges
    boxplot.x_range.factors = list(x)
    sigma_plot.x_range.factors = list(x)
    s10_plot.x_range.factors = list(x)
    s2_plot.x_range.factors = list(x)

    # Update source
    source.data = dict(
        x = x,
        sigma = line["sigma"],
        s10 = line["s10"],
        s2 = line["s2"],
        min = line["min"],
        quantile25 = line["quantile25"],
        quantile50 = line["quantile50"],
        quantile75 = line["quantile75"],
        max = line["max"],
        mu = line["mu"]
    )

# Draw the different plots (on a blank figure)

def gen_boxplot(plot):
    # (based on : https://docs.bokeh.org/en/latest/docs/gallery/boxplot.html)

    # Stems
    plot.segment(x0="x", y0="max", x1="x", y1="quantile75", source=source,
    line_color="black")
    plot.segment(x0="x", y0="min", x1="x", y1="quantile25", source=source,
    line_color="black")

    # Boxes
    plot.vbar(x="x", width=0.5, top="quantile75", bottom="quantile50", source=source,
    line_color="black", fill_color="#3B8686")
    plot.vbar(x="x", width=0.5, top="quantile50", bottom="quantile25", source=source,
    line_color="black", fill_color="#E08E79")

    # Other
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None

def gen_sigma_plot(plot):
    plot.vbar(x="x", top="sigma", source=source, width=0.5)
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None

def gen_s10_plot(plot):
    plot.vbar(x="x", top="s10", source=source, width=0.5)
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None

def gen_s2_plot(plot):
    plot.vbar(x="x", top="s2", source=source, width=0.5)
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None


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


    # Setup Bokeh server

curdoc().title = "Verificarlo Report"


    # Selection setup (initially, we select the first test/var/backend combination)

tests = data.index.get_level_values("test").drop_duplicates().tolist()
current_test = tests[0]

vars = data.loc[current_test].index.get_level_values("variable").drop_duplicates().tolist()
current_var = vars[0]

backends = data.loc[current_test, current_var].index.get_level_values("vfc_backend").drop_duplicates().tolist()
current_backend = backends[0]



    # Main ColumnDataSource setup
    # (all updates will simply be made to this object)

line = data.loc[current_test, current_var, current_backend]
x = gen_x_series(line["timestamp"])
source = ColumnDataSource(data=dict(
    x = x,
    sigma = line["sigma"],
    s10 = line["s10"],
    s2 = line["s2"],
    min = line["min"],
    quantile25 = line["quantile25"],
    quantile50 = line["quantile50"],
    quantile75 = line["quantile75"],
    max = line["max"],
    mu = line["mu"]
))



    # Plots setup

# Box plot
boxplot = figure(
    name="boxplot", title="Variable distribution over runs",
    plot_width=800, plot_height=300, x_range=x
)
gen_boxplot(boxplot)
curdoc().add_root(boxplot)

# Sigma plot (bar plot)
sigma_plot = figure(
    name="sigma_plot", title="Standard deviation σ over runs",
    plot_width=800, plot_height=300, x_range=x
)
gen_sigma_plot(sigma_plot)
curdoc().add_root(sigma_plot)

# s plot (bar plot with 2 tabs)
s10_plot = figure(
    name="s10_plot", title="Significant digits s over runs",
    plot_width=800, plot_height=300, x_range=x
)
gen_s10_plot(s10_plot)
s10_tab = Panel(child=s10_plot, title="Base 10")

s2_plot = figure(
    name="s2_plot", title="Significant digits s over runs",
    plot_width=800, plot_height=300, x_range=x
)

s2_tab = Panel(child=s2_plot, title="Base 2")
gen_s2_plot(s2_plot)
s_tabs = Tabs(name = "s_tabs", tabs=[s10_tab, s2_tab], tabs_location = "below")

curdoc().add_root(s_tabs)



    # Widgets setup

select_test = Select(
    name="select_test", title="Test :",
    value=current_test, options=tests
)
curdoc().add_root(select_test)

select_var = Select(
    name="select_var", title="Variable :",
    value=current_var, options=vars
)
curdoc().add_root(select_var)

select_backend = Select(
    name="select_backend", title="Verificarlo backend :",
    value=current_backend, options=backends
)
curdoc().add_root(select_backend)



    # Callbacks setups

def update_test(attrname, old, new):
    global current_test, current_var, current_backend

    # Update test selection
    current_test = new

    # Reset var selection
    vars = data.loc[current_test].index.get_level_values("variable").drop_duplicates().tolist()
    current_var = vars[0]
    select_var.value = current_var

    # Reset backend selection
    backends = data.loc[current_test, current_var].index.get_level_values("vfc_backend").drop_duplicates().tolist()
    current_backend = backends[0]
    select_backend.value = current_backend

    update_plots()

select_test.on_change("value", update_test)


def update_var(attrname, old, new):
    global current_test, current_var, current_backend

    # Update var selection
    current_var = new

    # Reset backend selection
    backends = data.loc[current_test, current_var].index.get_level_values("vfc_backend").drop_duplicates().tolist()
    current_backend = backends[0]
    select_backend.value = current_backend

    update_plots()

select_var.on_change("value", update_var)


def update_backend(attrname, old, new):
    global current_test, current_var, current_backend

    # Update backend selection
    current_backend = new

    update_plots()

select_backend.on_change("value", update_backend)
