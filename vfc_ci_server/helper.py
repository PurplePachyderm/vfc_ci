# Helper functions for the Bokeh server

import datetime

import pandas as pd

from bokeh.plotting import figure, show, curdoc
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.models import Select, ColumnDataSource, Panel, Tabs, HoverTool, OpenURL, TapTool


import selection_variables as selec


# From a timestamp, return the associated metadata as a Pandas serie
def get_metadata(timestamp):
    return selec.metadata.loc[timestamp]



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

    n = selec.current_n_runs

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
def update_runs_plots():
    line = selec.data.loc[selec.current_test, selec.current_var, selec.current_backend]
    x, x_metadata = gen_x_series(line["timestamp"])

    # Update x_ranges
    boxplot.x_range.factors = list(x)
    sigma_plot.x_range.factors = list(x)
    s10_plot.x_range.factors = list(x)
    s2_plot.x_range.factors = list(x)

    # Update selec.runs_source
    selec.runs_source.data = dict(
        x = x[-selec.current_n_runs:],
        is_git_commit = x_metadata["is_git_commit"][-selec.current_n_runs:],
        date = x_metadata["date"][-selec.current_n_runs:],
        hash = x_metadata["hash"][-selec.current_n_runs:],
        author = x_metadata["author"][-selec.current_n_runs:],
        message = x_metadata["message"][-selec.current_n_runs:],

        sigma = line["sigma"][-selec.current_n_runs:],
        s10 = line["s10"][-selec.current_n_runs:],
        s2 = line["s2"][-selec.current_n_runs:],
        min = line["min"][-selec.current_n_runs:],
        quantile25 = line["quantile25"][-selec.current_n_runs:],
        quantile50 = line["quantile50"][-selec.current_n_runs:],
        quantile75 = line["quantile75"][-selec.current_n_runs:],
        max = line["max"][-selec.current_n_runs:],
        mu = line["mu"][-selec.current_n_runs:]
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

    if selec.git_repo_linked:
        tap = TapTool(callback=OpenURL(url=selec.commit_link))
        plot.add_tools(tap)

    # Stems
    plot.segment(x0="x", y0="max", x1="x", y1="quantile75", source=selec.runs_source,
    line_color="black")
    plot.segment(x0="x", y0="min", x1="x", y1="quantile25", source=selec.runs_source,
    line_color="black")

    # Boxes
    plot.vbar(x="x", width=0.5, top="quantile75", bottom="quantile50", source=selec.runs_source,
    line_color="black", fill_color="#D20000")
    plot.vbar(x="x", width=0.5, top="quantile50", bottom="quantile25", source=selec.runs_source,
    line_color="black", fill_color="#008000")

    # Mu dot
    plot.dot(x="x", y="mu", size=30, source=selec.runs_source,
    color="black", legend_label="Empirical average μ")

    # Other
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None


# Can be used for any boxplot
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

    if selec.git_repo_linked:
        tap = TapTool(callback=OpenURL(url=selec.commit_link))
        plot.add_tools(tap)

    plot.vbar(x="x", top=data_field, source=selec.runs_source, width=0.5, color="#008000")
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None
