# Manage the view comparing a variable over different runs

import datetime

import pandas as pd

from math import pi

from bokeh.plotting import figure, show, curdoc
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.models import Select, ColumnDataSource, Panel, Tabs, HoverTool, \
TextInput, OpenURL, TapTool, Range, CustomJS

import helper

################################################################################



class CompareRuns:

        # Helper functions related to CompareRuns

    # From an array of timestamps, returns the array of runs names (for the x
    # axis ticks), as well as the metadata (in a dict of arrays) associated to
    # this array (for the tooltips)
    def gen_x_series(self, timestamps):

        # Initialize the objects to return
        x = []
        x_metadata = dict(
            date = [],
            is_git_commit = [],
            hash = [],
            author = [],
            message = []
        )

        # n==0 means we want all runs, we also make sure not to go out of bound
        # if asked for more runs than we have
        n = self.current_n_runs
        if n == 0 or n > len(timestamps):
            n = len(timestamps)


        for i in range(0, n):
            # Get metadata associated to this run
            row_metadata = helper.get_metadata(self.metadata, timestamps[-i-1])
            date = datetime.datetime.fromtimestamp(timestamps[-i-1]).isoformat()

            # Fill the x series
            str = helper.get_run_name(timestamps[-i-1], row_metadata["hash"])
            x.insert(0, helper.get_metadata(self.metadata, timestamps[-i-1])["name"])

            # Fill the metadata lists
            x_metadata["date"].insert(0, date)
            x_metadata["is_git_commit"].insert(0, row_metadata["is_git_commit"])
            x_metadata["hash"].insert(0, row_metadata["hash"])
            x_metadata["author"].insert(0, row_metadata["author"])
            x_metadata["message"].insert(0, row_metadata["message"])


        helper.reset_tick_strings()

        return x, x_metadata


    # Update plots based on current_test/var/backend combination
    def update_plots(self):
        loc = self.data.loc[[self.current_test], self.current_var, self.current_backend]

        timestamps = loc["timestamp"]

        x, x_metadata = self.gen_x_series(timestamps.sort_values())

        # Update x_ranges
        self.boxplot.x_range.factors = list(x)
        self.sigma_plot.x_range.factors = list(x)
        self.s10_plot.x_range.factors = list(x)
        self.s2_plot.x_range.factors = list(x)


        # Update source

        # Select the last n runs only, and make sure each entry is a list
        n = self.current_n_runs
        self.source.data = dict(
            # Metadata
            x = x[-n:],
            is_git_commit = x_metadata["is_git_commit"][-n:],
            date = x_metadata["date"][-n:],
            hash = x_metadata["hash"][-n:],
            author = x_metadata["author"][-n:],
            message = x_metadata["message"][-n:],

            # Data
            sigma = loc["sigma"][-n:],
            s10 = loc["s10"][-n:],
            s2 = loc["s2"][-n:],
            min = loc["min"][-n:],
            quantile25 = loc["quantile25"][-n:],
            quantile50 = loc["quantile50"][-n:],
            quantile75 = loc["quantile75"][-n:],
            max = loc["max"][-n:],
            mu = loc["mu"][-n:],
            nruns = loc["nruns"][-n:]
        )



        # Plots generation function

    def gen_boxplot(self, plot):
        # (based on: https://docs.bokeh.org/en/latest/docs/gallery/boxplot.html)

        hover = HoverTool(tooltips = [
            ("Git commit", "@is_git_commit"),
            ("Date", "@date"),
            ("Hash", "@hash"),
            ("Author", "@author"),
            ("Message", "@message"),
            ("Min", "@min{0.*f}"),
            ("Max", "@max{0.*f}"),
            ("1st quartile", "@quantile25{0.*f}"),
            ("Median", "@quantile50{0.*f}"),
            ("3rd quartile", "@quantile75{0.*f}"),
            ("μ", "@mu{0.*f}"),
            ("Number of samples", "@nruns")
        ])
        plot.add_tools(hover)

        # Custom JS callback that will be used when tapping on a run
        # Only switches the view, a server callback is required to update plots
        # (defined inside template to avoid bloating server w/ too much JS code)
        tap_callback_js = "goToInspectRuns();"
        tap = TapTool(callback=CustomJS(code=tap_callback_js))
        plot.add_tools(tap)


        # Stems
        top_stem = plot.segment(
            x0="x", y0="max", x1="x", y1="quantile75",
            source=self.source, line_color="black"
        )
        top_stem.data_source.selected.on_change("indices", self.inspect_run_callback)

        bottom_stem = plot.segment(
            x0="x", y0="min", x1="x", y1="quantile25",
            source=self.source, line_color="black"
        )
        bottom_stem.data_source.selected.on_change("indices", self.inspect_run_callback)


        # Boxes
        top_box = plot.vbar(
            x="x", width=0.5, top="quantile75", bottom="quantile50",
            source=self.source, line_color="black"
        )
        top_box.data_source.selected.on_change("indices", self.inspect_run_callback)

        bottom_box = plot.vbar(
            x="x", width=0.5, top="quantile50", bottom="quantile25",
            source=self.source, line_color="black"
        )
        bottom_box.data_source.selected.on_change("indices", self.inspect_run_callback)


        # Mu dot
        mu_dot = plot.dot(
            x="x", y="mu", size=30, source=self.source,
            color="black", legend_label="Empirical average μ"
        )
        mu_dot.data_source.selected.on_change("indices", self.inspect_run_callback)


        # Other
        plot.xgrid.grid_line_color = None
        plot.ygrid.grid_line_color = None

        plot.yaxis[0].formatter.power_limit_high = 0
        plot.yaxis[0].formatter.power_limit_low = 0
        plot.yaxis[0].formatter.precision = 3

        plot.xaxis[0].major_label_orientation = pi/8


    def gen_bar_plot(self, plot, data_field, display_name):
        hover = HoverTool(tooltips = [
            ("Git commit", "@is_git_commit"),
            ("Date", "@date"),
            ("Hash", "@hash"),
            ("Author", "@author"),
            ("Message", "@message"),
            (display_name, "@" + data_field),
            ("Number of samples", "@nruns")
        ])
        plot.add_tools(hover)

        # Custom JS callback that will be used when tapping on a run
        # Only switches the view, a server callback is required to update plots
        # (defined inside template to avoid bloating server w/ too much JS code)
        tap_callback_js = "goToInspectRuns();"
        tap = TapTool(callback=CustomJS(code=tap_callback_js))
        plot.add_tools(tap)

        bar = plot.vbar(
            x="x", top=data_field, source=self.source,
            width=0.5
        )
        bar.data_source.selected.on_change("indices", self.inspect_run_callback)
        plot.xgrid.grid_line_color = None
        plot.ygrid.grid_line_color = None

        plot.yaxis[0].formatter.power_limit_high = 0
        plot.yaxis[0].formatter.power_limit_low = 0
        plot.yaxis[0].formatter.precision = 3

        plot.xaxis[0].major_label_orientation = pi/8



        # Widgets' callback functions

    def update_test(self, attrname, old, new):

        # Update test selection
        self.current_test = new


        self.vars = data.loc[self.current_test]\
        .index.get_level_values("variable").drop_duplicates().tolist()

        # Reset var selection if old one is not available in new vars
        if self.current_var not in self.vars:
            self.current_var = self.vars[0]
            self.select_var.value = self.current_var


        self.backends = self.data.loc[self.current_test, self.current_var]\
        .index.get_level_values("vfc_backend").drop_duplicates().tolist()

        # Reset backend selection if old one is not available in new backends
        if self.current_backend not in self.backends:
            self.current_backend = self.backends[0]
            self.select_backend.value = self.current_backend

        self.update_plots()


    def update_var(self, attrname, old, new):

        # Update var selection
        self.current_var = new


        self.backends = self.data.loc[self.current_test, self.current_var]\
        .index.get_level_values("vfc_backend").drop_duplicates().tolist()

        # Reset backend selection if old one is not available in new backends
        if self.current_backend not in self.backends:
            self.current_backend = self.backends[0]
            self.select_backend.value = self.current_backend

        self.update_plots()


    def update_backend(self, attrname, old, new):
        # Simply update backend selection
        self.current_backend = new
        self.update_plots()


    def update_n_runs(self, attrname, old, new):
        # Simply update runs selection (value and string display)
        self.current_n_runs_display = new
        self.current_n_runs = self.n_runs_dict[self.current_n_runs_display]

        self.update_plots()



        # Setup functions

    # Setup all initial selections (and possible selections)
    def setup_selection(self):

        # Test/var/backend combination (we select all first elements at init)
        self.tests = self.data.index.get_level_values("test").drop_duplicates().tolist()
        self.current_test = self.tests[0]

        self.vars = self.data.loc[self.current_test]\
        .index.get_level_values("variable").drop_duplicates().tolist()
        self.current_var = self.vars[0]

        self.backends = self.data.loc[self.current_test, self.current_var]\
        .index.get_level_values("vfc_backend").drop_duplicates().tolist()

        self.current_backend = self.backends[0]


        # Number of runs to display
        # The dict structure allows to get int value from the display string
        # in O(1)
        self.n_runs_dict = {
            "Last 3 runs": 3,
            "Last 5 runs": 5,
            "Last 10 runs": 10,
            "All runs": 0
        }

        # Contains all options strings
        self.n_runs_display = list(self.n_runs_dict.keys())

        # Will be used when updating plots (contains actual number)
        self.current_n_runs = self.n_runs_dict[self.n_runs_display[1]]

        # Contains the selected option string, used to update current_n_runs
        self.current_n_runs_display = self.n_runs_display[1]


    # Create all plots
    def setup_plots(self):

        tools = "pan, wheel_zoom, xwheel_zoom, ywheel_zoom, reset, save"

        # Box plot
        self.boxplot = figure(
            name="boxplot", title="Variable distribution over runs",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode="scale_width"
        )

        self.gen_boxplot(self.boxplot)
        self.doc.add_root(self.boxplot)


        # Sigma plot (bar plot)
        self.sigma_plot = figure(
            name="sigma_plot", title="Standard deviation σ over runs",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode='scale_width'
        )

        self.gen_bar_plot(self.sigma_plot, "sigma", "σ")
        self.doc.add_root(self.sigma_plot)


        # s plot (bar plot with 2 tabs)
        self.s10_plot = figure(
            name="s10_plot", title="Significant digits s over runs",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode='scale_width'
        )
        self.gen_bar_plot(self.s10_plot, "s10", "s")
        s10_tab = Panel(child=self.s10_plot, title="Base 10")

        self.s2_plot = figure(
            name="s2_plot", title="Significant digits s over runs",
            plot_width=900, plot_height=400, x_range=[""], y_range=(-2.5, 53),
            tools=tools, sizing_mode='scale_width'
        )
        self.gen_bar_plot(self.s2_plot, "s2", "s")
        s2_tab = Panel(child=self.s2_plot, title="Base 2")

        s_tabs = Tabs(name = "s_tabs", tabs=[s10_tab, s2_tab], tabs_location = "below")

        self.doc.add_root(s_tabs)


    # Create all widgets
    def setup_widgets(self):

        # Custom JS callback that will be used client side to filter selections
        filter_callback_js = """
        selector.options = options.filter(e => !e.indexOf(cb_obj.value));
        """


        # Test
        self.select_test = Select(
            name="select_test", title="Test :",
            value=self.current_test, options=self.tests
        )
        self.doc.add_root(self.select_test)
        self.select_test.on_change("value", self.update_test)

        test_filter = TextInput(
            name="test_filter", title="Tests filter:"
        )
        test_filter.js_on_change("value", CustomJS(
            args=dict(options=self.tests, selector=self.select_test),
            code=filter_callback_js
        ))
        self.doc.add_root(test_filter)


        # Variable
        self.select_var = Select(
            name="select_var", title="Variable :",
            value=self.current_var, options=self.vars
        )
        self.doc.add_root(self.select_var)
        self.select_var.on_change("value", self.update_var)

        var_filter = TextInput(
            name="var_filter", title="Variables filter:"
        )
        var_filter.js_on_change("value", CustomJS(
            args=dict(options=self.vars, selector=self.select_var),
            code=filter_callback_js
        ))
        self.doc.add_root(var_filter)


        # Backend
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



        # Communication methods
        # (to send/receive messages to/from master)

    # Callback to change view of Inspect runs when data is selected
    def inspect_run_callback(self, attr, old, new):

        # In case we just unselected everything, then do nothing
        if new == []:
            return

        index = new[-1]
        run_name = self.source.data["x"][index]

        self.master.go_to_inspect(run_name)



        # Constructor

    def __init__(self, master, doc, data, metadata, git_repo_linked, commit_link):

        self.master = master

        self.doc = doc
        self.data = data
        self.metadata = metadata
        self.git_repo_linked = git_repo_linked
        self.commit_link = commit_link

        # Will be filled/updated in update_plots()
        self.source = ColumnDataSource(data={})


        # Setup everything
        self.setup_selection()
        self.setup_plots()
        self.setup_widgets()


        # At this point, everything should have been initialized, so we can
        # show the plots for the first time
        self.update_plots()
