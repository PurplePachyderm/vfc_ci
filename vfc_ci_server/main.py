# Look for and read all the run files in the current directory (ending with
# .vfcrun.hd5), and lanch a Bokeh server for the visualization of this data.

import os
import json
import datetime
import sys

import pandas as pd

from bokeh.plotting import figure, show, curdoc
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.models import Select, ColumnDataSource, Panel, Tabs, HoverTool, OpenURL, TapTool

from jinja2 import Environment, FileSystemLoader


################################################################################


        # HELPER FUNCTIONS

# From a timestamp, return the associated metadata as a Pandas serie
def get_metadata(timestamp):
    return metadata.loc[timestamp]



# From an array of timestamps, return an array of hashes/dates that can
# be used as the x series of a bar/box plot, as well as the metadata (in a dict
# of arrays) associated to this x series (for the tooltips)
def gen_x_series(timestamps):
    x = []
    x_metadata = dict(
        date = [],
        is_git_commit = [],
        hash = [],
        author = [],
        message = []
    )

    n = current_n_runs

    if n == 0 or n > len(timestamps):
        n = len(timestamps)

    for i in range(0, n):
        row_metadata = get_metadata(timestamps[-i-1])
        date = datetime.datetime.fromtimestamp(timestamps[-i-1]).isoformat()

        if row_metadata["is_git_commit"]:
            x.insert(0, row_metadata["hash"])

        else:
            x.insert(0, date)

        # Fill the metadata lists
        x_metadata["date"].insert(0, date)
        x_metadata["is_git_commit"].insert(0, row_metadata["is_git_commit"])
        x_metadata["hash"].insert(0, row_metadata["hash"])
        x_metadata["author"].insert(0, row_metadata["author"])
        x_metadata["message"].insert(0, row_metadata["message"])

    return x, x_metadata



# Update plots based on current_test/var/backend combination
def update_plots():
    loc = data.loc[current_test, current_var, current_backend]
    x, x_metadata = gen_x_series(loc["timestamp"])

    # Update x_ranges
    boxplot.x_range.factors = list(x)
    sigma_plot.x_range.factors = list(x)
    s10_plot.x_range.factors = list(x)
    s2_plot.x_range.factors = list(x)

    # Update source
    source.data = dict(
        x = x[-current_n_runs:],
        is_git_commit = x_metadata["is_git_commit"][-current_n_runs:],
        date = x_metadata["date"][-current_n_runs:],
        hash = x_metadata["hash"][-current_n_runs:],
        author = x_metadata["author"][-current_n_runs:],
        message = x_metadata["message"][-current_n_runs:],

        sigma = loc["sigma"][-current_n_runs:],
        s10 = loc["s10"][-current_n_runs:],
        s2 = loc["s2"][-current_n_runs:],
        min = loc["min"][-current_n_runs:],
        quantile25 = loc["quantile25"][-current_n_runs:],
        quantile50 = loc["quantile50"][-current_n_runs:],
        quantile75 = loc["quantile75"][-current_n_runs:],
        max = loc["max"][-current_n_runs:],
        mu = loc["mu"][-current_n_runs:]
    )


    # Draw the different plots (on a blank figure)

def gen_boxplot(plot):
    # (based on : https://docs.bokeh.org/en/latest/docs/gallery/boxplot.html)

    hover = HoverTool(tooltips = [
        ("Git commit", "@is_git_commit"),
        ("Date", "@date"),
        ("Hash", "@hash"),
        ("Author", "@author"),
        ("Message", "@message"),
        ("Min", "@min"),
        ("Max", "@max"),
        ("1st quartile", "@quantile25"),
        ("Median", "@quantile50"),
        ("3rd quartile", "@quantile75"),
        ("μ", "@mu")
    ])
    plot.add_tools(hover)

    if git_repo_linked:
        tap = TapTool(callback=OpenURL(url=commit_link))
        plot.add_tools(tap)

    # Stems
    plot.segment(x0="x", y0="max", x1="x", y1="quantile75", source=source,
    line_color="black")
    plot.segment(x0="x", y0="min", x1="x", y1="quantile25", source=source,
    line_color="black")

    # Boxes
    plot.vbar(x="x", width=0.5, top="quantile75", bottom="quantile50", source=source,
    line_color="black", fill_color="#D20000")
    plot.vbar(x="x", width=0.5, top="quantile50", bottom="quantile25", source=source,
    line_color="black", fill_color="#008000")

    # Mu dot
    plot.dot(x="x", y="mu", size=30, source=source,
    color="black", legend_label="Empirical average μ")

    # Other
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None


def gen_bar_plot(plot, data_field, display_name):
    hover = HoverTool(tooltips = [
        ("Git commit", "@is_git_commit"),
        ("Date", "@date"),
        ("Hash", "@hash"),
        ("Author", "@author"),
        ("Message", "@message"),
        (display_name, "@" + data_field)
    ])
    plot.add_tools(hover)

    if git_repo_linked:
        tap = TapTool(callback=OpenURL(url=commit_link))
        plot.add_tools(tap)

    plot.vbar(x="x", top=data_field, source=source, width=0.5, color="#008000")
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None



################################################################################


    # READ VFCRUN FILES

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



################################################################################


    # SETUP BOKEH SERVER

curdoc().title = "Verificarlo Report"


    # Look for the Git repository remote address
    # (if a Git repo is specified, the webpage will contain hyperlinks to the
    # repository and the different commits)

git_repo_linked = False

if len(sys.argv) == 3:
    from urllib.parse import urlparse

    method = sys.argv[1]
    address = sys.argv[2]
    url = ""


    # Here, address is either the remote URL or the path to the local Git repo
    # (depending on the method)

    if method == "remote":
        # We should directly have a Git URL
        url = address

    elif method == "directory":
        # Fetch the remote URL from the local repo
        from git import Repo
        repo = Repo(address)
        url = repo.remotes.origin.url

    else:
        raise ValueError("The specified method to get the Git repository is "\
        "invalid. Are you calling Bokeh directly instead of using the "\
        "Verificarlo wrapper ?")


    # At this point, "url" should be set correctly, we can get the repo's
    # URL and name

    parsed_url = urlparse(url)

    path = parsed_url.path.split("/")
    if len(path) < 3:
        raise ValueError("The found URL doesn't seem to be pointing to a Git "\
        "repository (path is too short)")

    repo_name = path[2]

    curdoc().template_variables["repo_url"] = url
    curdoc().template_variables["repo_name"] = repo_name


    # We should have a "github.com" or a "*gitlab*" URL

    if parsed_url.netloc == "github.com":
        commit_link = "https://" + parsed_url.netloc + parsed_url.path + "/commit/@hash"
        curdoc().template_variables["commit_link"] = commit_link
        curdoc().template_variables["git_host"] = "GitHub"
        git_repo_linked = True

    elif "gitlab" in parsed_url.netloc:
        commit_link = "https://" + parsed_url.netloc + parsed_url.path + "/-/commit/@hash"
        curdoc().template_variables["git_host"] = "GitLab"
        git_repo_linked = True

    else:
        raise ValueError("The found URL doesn't seem to be a GitHub or GitLab URL")


curdoc().template_variables["git_repo_linked"] = git_repo_linked



################################################################################


    # RUNS COMPARISON
    # TODO Move this to the dedicated file

    # Selection setup (initially, we select the first test/var/backend combination)

tests = data.index.get_level_values("test").drop_duplicates().tolist()
current_test = tests[0]

vars = data.loc[current_test].index.get_level_values("variable").drop_duplicates().tolist()
current_var = vars[0]

backends = data.loc[current_test, current_var].index.get_level_values("vfc_backend").drop_duplicates().tolist()
current_backend = backends[0]

# Number of runs to display
n_runs = {
    "Last 3 runs": 3,
    "Last 5 runs": 5,
    "Last 10 runs": 10,
    "All runs": 0
}
n_runs_display = list(n_runs.keys())

current_n_runs = n_runs[n_runs_display[1]]
current_n_runs_display = n_runs_display[1]



    # Plots setup

source = ColumnDataSource(data={})

tools = "pan, wheel_zoom, xwheel_zoom, ywheel_zoom, reset, save"

# Box plot
boxplot = figure(
    name="boxplot", title="Variable distribution over runs",
    plot_width=800, plot_height=330, x_range=[""],
    tools=tools
)
gen_boxplot(boxplot)
curdoc().add_root(boxplot)

# Sigma plot (bar plot)
sigma_plot = figure(
    name="sigma_plot", title="Standard deviation σ over runs",
    plot_width=800, plot_height=330, x_range=[""],
    tools=tools
)
gen_bar_plot(sigma_plot, "sigma", "σ")
curdoc().add_root(sigma_plot)

# s plot (bar plot with 2 tabs)
s10_plot = figure(
    name="s10_plot", title="Significant digits s over runs",
    plot_width=800, plot_height=330, x_range=[""],
    tools=tools
)
gen_bar_plot(s10_plot, "s10", "s")
s10_tab = Panel(child=s10_plot, title="Base 10")

s2_plot = figure(
    name="s2_plot", title="Significant digits s over runs",
    plot_width=800, plot_height=330, x_range=[""],
    tools=tools
)
gen_bar_plot(s2_plot, "s2", "s")
s2_tab = Panel(child=s2_plot, title="Base 2")

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

# Number of runs to display
select_n_runs = Select(
    name="select_n_runs", title="Display :",
    value=current_n_runs_display, options=n_runs_display
)
curdoc().add_root(select_n_runs)



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


def update_n_runs(attrname, old, new):
    global current_n_runs_display, current_n_runs

    current_n_runs_display = new
    current_n_runs = n_runs[current_n_runs_display]

    update_plots()

select_n_runs.on_change("value", update_n_runs)



    # Init plots

update_plots()



################################################################################


    # WIP VARIABLES COMPARISON

import compare_variables

compare_variables.doc = curdoc()
compare_variables.foo()
