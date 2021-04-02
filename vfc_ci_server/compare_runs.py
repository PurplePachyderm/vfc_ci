# This file makes it possible to compare a single variable over different runs
# TODO : Move code from main to this file

import datetime

import pandas as pd

from bokeh.plotting import figure, show, curdoc
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.models import Select, ColumnDataSource, Panel, Tabs, HoverTool, OpenURL, TapTool



################################################################################


class CompareRuns:


        # Helper functions

    # From a timestamp, return the associated metadata as a Pandas serie
    def get_metadata(self, timestamp):
        return self.metadata.loc[timestamp]


    # From an array of timestamps, return an array of hashes/dates that can
    # be used as the x series of a bar/box plot, as well as the metadata (in a dict
    # of arrays) associated to this x series (for the tooltips)
    def gen_x_series(self, timestamps):
        x = []
        x_metadata = dict(
            date = [],
            is_git_commit = [],
            hash = [],
            author = [],
            message = []
        )

        n = self.current_n_runs

        if n == 0 or n > len(timestamps):
            n = len(timestamps)

        for i in range(0, n):
            row_metadata = self.get_metadata(timestamps[-i-1])
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
    def update_plots(self):
        loc = self.data.loc[self.current_test, self.current_var, self.current_backend]
        x, x_metadata = self.gen_x_series(loc["timestamp"])

        # Update x_ranges
        self.boxplot.x_range.factors = list(x)
        self.sigma_plot.x_range.factors = list(x)
        self.s10_plot.x_range.factors = list(x)
        self.s2_plot.x_range.factors = list(x)

        # Update source
        n = self.current_n_runs
        self.source.data = dict(
            x = x[-n:],
            is_git_commit = x_metadata["is_git_commit"][-n:],
            date = x_metadata["date"][-n:],
            hash = x_metadata["hash"][-n:],
            author = x_metadata["author"][-n:],
            message = x_metadata["message"][-n:],

            sigma = loc["sigma"][-n:],
            s10 = loc["s10"][-n:],
            s2 = loc["s2"][-n:],
            min = loc["min"][-n:],
            quantile25 = loc["quantile25"][-n:],
            quantile50 = loc["quantile50"][-n:],
            quantile75 = loc["quantile75"][-n:],
            max = loc["max"][-n:],
            mu = loc["mu"][-n:]
        )



        # Plots generation function

    def gen_boxplot(self, plot):
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

        if self.git_repo_linked:
            tap = TapTool(callback=OpenURL(url=self.commit_link))
            plot.add_tools(tap)

        # Stems
        plot.segment(x0="x", y0="max", x1="x", y1="quantile75",
        source=self.source, line_color="black")
        plot.segment(x0="x", y0="min", x1="x", y1="quantile25",
        source=self.source, line_color="black")

        # Boxes
        plot.vbar(x="x", width=0.5, top="quantile75", bottom="quantile50",
        source=self.source, line_color="black", fill_color="#D20000")
        plot.vbar(x="x", width=0.5, top="quantile50", bottom="quantile25",
        source=self.source, line_color="black", fill_color="#008000")

        # Mu dot
        plot.dot(x="x", y="mu", size=30, source=self.source,
        color="black", legend_label="Empirical average μ")

        # Other
        plot.xgrid.grid_line_color = None
        plot.ygrid.grid_line_color = None


    def gen_bar_plot(self, plot, data_field, display_name):
        hover = HoverTool(tooltips = [
            ("Git commit", "@is_git_commit"),
            ("Date", "@date"),
            ("Hash", "@hash"),
            ("Author", "@author"),
            ("Message", "@message"),
            (display_name, "@" + data_field)
        ])
        plot.add_tools(hover)

        if self.git_repo_linked:
            tap = TapTool(callback=OpenURL(url=self.commit_link))
            plot.add_tools(tap)

        plot.vbar(x="x", top=data_field, source=self.source, width=0.5,
        color="#008000")
        plot.xgrid.grid_line_color = None
        plot.ygrid.grid_line_color = None



        # Widgets' callback functions

    def update_test(self, attrname, old, new):

        # Update test selection
        self.current_test = new

        # Reset var selection
        vars = data.loc[self.current_test]\
        .index.get_level_values("variable").drop_duplicates().tolist()

        self.current_var = vars[0]
        self.select_var.value = self.current_var

        # Reset backend selection
        backends = self.data.loc[self.current_test, self.current_var]\
        .index.get_level_values("vfc_backend").drop_duplicates().tolist()

        self.current_backend = backends[0]
        self.select_backend.value = self.current_backend

        self.update_plots()


    def update_var(self, attrname, old, new):

        # Update var selection
        self.current_var = new

        # Reset backend selection
        backends = self.data.loc[self.current_test, self.current_var]\
        .index.get_level_values("vfc_backend").drop_duplicates().tolist()

        self.current_backend = backends[0]
        self.select_backend.value = self.current_backend

        self.update_plots()


    def update_backend(self, attrname, old, new):

        # Update backend selection
        self.current_backend = new

        self.update_plots()


    def update_n_runs(self, attrname, old, new):

        self.current_n_runs_display = new
        self.current_n_runs = self.n_runs[self.current_n_runs_display]

        self.update_plots()



        # Setup functions

    # This function will setup all initial selections (and possible selections)
    def setup_selection(self):

        # Initially, we select the first test/var/backend combination
        self.tests = self.data.index.get_level_values("test").drop_duplicates().tolist()
        self.current_test = self.tests[0]

        self.vars = self.data.loc[self.current_test]\
        .index.get_level_values("variable").drop_duplicates().tolist()

        self.current_var = self.vars[0]

        self.backends = self.data.loc[self.current_test, self.current_var]\
        .index.get_level_values("vfc_backend").drop_duplicates().tolist()

        self.current_backend = self.backends[0]


        # Number of runs to display
        self.n_runs = {
            "Last 3 runs": 3,
            "Last 5 runs": 5,
            "Last 10 runs": 10,
            "All runs": 0
        }

        # Contains all options strings
        self.n_runs_display = list(self.n_runs.keys())

        # Will be used when updating plots (contains actual number)
        self.current_n_runs = self.n_runs[self.n_runs_display[1]]

        # Contains the selected option string, used to update current_n_runs
        self.current_n_runs_display = self.n_runs_display[1]


    # This function will create all plots
    def setup_plots(self):

        tools = "pan, wheel_zoom, xwheel_zoom, ywheel_zoom, reset, save"

        # Box plot
        self.boxplot = figure(
            name="boxplot", title="Variable distribution over runs",
            plot_width=800, plot_height=330, x_range=[""],
            tools=tools
        )

        self.gen_boxplot(self.boxplot)
        self.doc.add_root(self.boxplot)


        # Sigma plot (bar plot)
        self.sigma_plot = figure(
            name="sigma_plot", title="Standard deviation σ over runs",
            plot_width=800, plot_height=330, x_range=[""],
            tools=tools
        )

        self.gen_bar_plot(self.sigma_plot, "sigma", "σ")
        self.doc.add_root(self.sigma_plot)


        # s plot (bar plot with 2 tabs)
        self.s10_plot = figure(
            name="s10_plot", title="Significant digits s over runs",
            plot_width=800, plot_height=330, x_range=[""],
            tools=tools
        )


        self.gen_bar_plot(self.s10_plot, "s10", "s")
        s10_tab = Panel(child=self.s10_plot, title="Base 10")

        self.s2_plot = figure(
            name="s2_plot", title="Significant digits s over runs",
            plot_width=800, plot_height=330, x_range=[""],
            tools=tools
        )

        self.gen_bar_plot(self.s2_plot, "s2", "s")
        s2_tab = Panel(child=self.s2_plot, title="Base 2")

        s_tabs = Tabs(name = "s_tabs", tabs=[s10_tab, s2_tab], tabs_location = "below")

        self.doc.add_root(s_tabs)


    # This function will create all widgets
    def setup_widgets(self):

        # Test -> variable -> backend selection
        self.select_test = Select(
            name="select_test", title="Test :",
            value=self.current_test, options=self.tests
        )

        self.doc.add_root(self.select_test)
        self.select_test.on_change("value", self.update_test)

        self.select_var = Select(
            name="select_var", title="Variable :",
            value=self.current_var, options=self.vars
        )

        self.doc.add_root(self.select_var)
        self.select_var.on_change("value", self.update_var)

        self.select_backend = Select(
            name="select_backend", title="Verificarlo backend :",
            value=self.current_backend, options=self.backends
        )

        self.doc.add_root(self.select_backend)
        self.select_backend.on_change("value", self.update_backend)


        # Number of runs to display
        self.select_n_runs = Select(
            name="select_n_runs", title="Display :",
            value=self.current_n_runs_display, options=self.n_runs_display
        )

        self.doc.add_root(self.select_n_runs)
        self.select_n_runs.on_change("value", self.update_n_runs)


        # At this point, everything should have been iitialized, so we can print
        # the plots for the first time
        self.update_plots()



        # Constructor

    def __init__(self, doc, data, metadata, git_repo_linked, commit_link):

        self.doc = doc
        self.data = data
        self.metadata = metadata
        self.git_repo_linked = git_repo_linked
        self.commit_link = commit_link

        self.source = ColumnDataSource(data={})

        # Setup everything
        self.setup_selection()
        self.setup_plots()
        self.setup_widgets()
