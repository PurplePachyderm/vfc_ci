# Manage the view comparing a variable over different runs

import time

import pandas as pd

from math import pi

from bokeh.plotting import figure, curdoc
from bokeh.embed import components
from bokeh.models import Select, ColumnDataSource, Panel, Tabs, HoverTool, \
TextInput, TapTool, CustomJS

import helper
import plot

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

        # n == 0 means we want all runs, we also make sure not to go out of
        # bound if asked for more runs than we have
        n = self.current_n_runs
        if n == 0 or n > len(timestamps):
            n = len(timestamps)


        for i in range(0, n):
            # Get metadata associated to this run
            row_metadata = helper.get_metadata(self.metadata, timestamps[-i-1])
            date = time.ctime(timestamps[-i-1])

            # Fill the x series
            str = row_metadata["name"]
            x.insert(0, helper.get_metadata(self.metadata, timestamps[-i-1])["name"])

            # Fill the metadata lists
            x_metadata["date"].insert(0, date)
            x_metadata["is_git_commit"].insert(0, row_metadata["is_git_commit"])
            x_metadata["hash"].insert(0, row_metadata["hash"])
            x_metadata["author"].insert(0, row_metadata["author"])
            x_metadata["message"].insert(0, row_metadata["message"])


        return x, x_metadata


    # Update plots based on current test/var/backend combination
    def update_plots(self):

        # Select all data matching current test/var/backend
        runs = self.data.loc[
            [self.select_test.value],
            self.select_var.value, self.select_backend.value
        ]

        timestamps = runs["timestamp"]

        x, x_metadata = self.gen_x_series(timestamps.sort_values())

        # Update x_ranges
        helper.reset_x_ranges(self.plots, list(x))


        # Update source

        # Select the last n runs only
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
            sigma = runs["sigma"][-n:],
            s10 = runs["s10"][-n:],
            s2 = runs["s2"][-n:],
            min = runs["min"][-n:],
            quantile25 = runs["quantile25"][-n:],
            quantile50 = runs["quantile50"][-n:],
            quantile75 = runs["quantile75"][-n:],
            max = runs["max"][-n:],
            mu = runs["mu"][-n:],
            pvalue = runs["pvalue"][-n:],
            nsamples = runs["nsamples"][-n:]
        )



        # Widgets' callback functions

    def update_test(self, attrname, old, new):

        # If the value is updated by the CustomJS, self.select_var.value won't
        # be updated, so we have to look for that case and assign it manually

        # new should be a list when updated by CustomJS
        if type(new) == list:
            new = new[0]

        if new != self.select_test.value:
            # The callback will be triggered again with the updated value
            self.select_test.value = new
            return

        # New list of available vars
        self.vars = self.data.loc[new]\
        .index.get_level_values("variable").drop_duplicates().tolist()
        self.select_var.options = self.vars


        # Reset var selection if old one is not available in new vars
        if self.select_var.value not in self.vars:
            self.select_var.value = self.vars[0]
            # The update_var callback will be triggered by the assignment

        else:
            # Trigger the callback manually (since the plots need to be updated
            # anyway)
            self.update_var("", "", self.select_var.value)


    def update_var(self, attrname, old, new):

        # If the value is updated by the CustomJS, self.select_var.value won't
        # be updated, so we have to look for that case and assign it manually

        # new should be a list when updated by CustomJS
        if type(new) == list:
            new = new[0]

        if new != self.select_var.value:
            # The callback will be triggered again with the updated value
            self.select_var.value = new
            return


        # New list of available backends
        self.backends = self.data.loc[self.select_test.value, self.select_var.value]\
        .index.get_level_values("vfc_backend").drop_duplicates().tolist()
        self.select_backend.options = self.backends

        # Reset backend selection if old one is not available in new backends
        if self.select_backend.value not in self.backends:
            self.select_backend.value = self.backends[0]
            # The update_backend callback will be triggered by the assignment

        else:
            # Trigger the callback manually (since the plots need to be updated
            # anyway)
            self.update_backend("", "", self.select_backend.value)


    def update_backend(self, attrname, old, new):

        # Simply update plots, since no other data is affected
        self.update_plots()


    def update_n_runs(self, attrname, old, new):
        # Simply update runs selection (value and string display)
        self.select_n_runs.value = new
        self.current_n_runs = self.n_runs_dict[self.select_n_runs.value]

        self.update_plots()



        # Bokeh setup functions

    def setup_plots(self):

        tools = "pan, wheel_zoom, xwheel_zoom, ywheel_zoom, reset, save"

        # Custom JS callback that will be used when tapping on a run
        # Only switches the view, a server callback is required to update plots
        # (defined inside template to avoid bloating server w/ too much JS code)
        js_tap_callback = "goToInspectRuns();"


        # Box plot
        self.plots["boxplot"] = figure(
            name="boxplot", title="Variable distribution over runs",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode="scale_width"
        )

        box_tooltips = [
            ("Git commit", "@is_git_commit"),
            ("Date", "@date"),
            ("Hash", "@hash"),
            ("Author", "@author"),
            ("Message", "@message"),
            ("Min", "@min{%0.18e}"),
            ("Max", "@max{%0.18e}"),
            ("1st quartile", "@quantile25{%0.18e}"),
            ("Median", "@quantile50{%0.18e}"),
            ("3rd quartile", "@quantile75{%0.18e}"),
            ("μ", "@mu{%0.18e}"),
            ("p-value", "@pvalue"),
            ("Number of samples", "@nsamples")
        ]
        box_tooltips_formatters = {
            "@min" : "printf",
            "@max" : "printf",
            "@quantile25" : "printf",
            "@quantile50" : "printf",
            "@quantile75" : "printf",
            "@mu" : "printf"
        }

        plot.fill_boxplot(
            self.plots["boxplot"], self.source,
            tooltips = box_tooltips,
            tooltips_formatters = box_tooltips_formatters,
            js_tap_callback = js_tap_callback,
            server_tap_callback = self.inspect_run_callback,
        )
        self.doc.add_root(self.plots["boxplot"])


        # Sigma plot (bar plot)
        self.plots["sigma_plot"] = figure(
            name="sigma_plot", title="Standard deviation σ over runs",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode="scale_width"
        )

        sigma_tooltips = [
            ("Git commit", "@is_git_commit"),
            ("Date", "@date"),
            ("Hash", "@hash"),
            ("Author", "@author"),
            ("Message", "@message"),
            ("σ", "@sigma"),
            ("Number of samples", "@nsamples")
        ]

        plot.fill_dotplot(
            self.plots["sigma_plot"], self.source, "sigma",
            tooltips = sigma_tooltips,
            js_tap_callback = js_tap_callback,
            server_tap_callback = self.inspect_run_callback,
            lines = True
        )
        self.doc.add_root(self.plots["sigma_plot"])


        # s plot (bar plot with 2 tabs)
        self.plots["s10_plot"] = figure(
            name="s10_plot", title="Significant digits s over runs",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode="scale_width"
        )

        s10_tooltips = [
            ("Git commit", "@is_git_commit"),
            ("Date", "@date"),
            ("Hash", "@hash"),
            ("Author", "@author"),
            ("Message", "@message"),
            ("s", "@s10"),
            ("Number of samples", "@nsamples")
        ]

        plot.fill_dotplot(
            self.plots["s10_plot"], self.source, "s10",
            tooltips = s10_tooltips,
            js_tap_callback = js_tap_callback,
            server_tap_callback = self.inspect_run_callback,
            lines = True
        )
        s10_tab = Panel(child=self.plots["s10_plot"], title="Base 10")


        self.plots["s2_plot"] = figure(
            name="s2_plot", title="Significant digits s over runs",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode="scale_width"
        )

        s2_tooltips = [
            ("Git commit", "@is_git_commit"),
            ("Date", "@date"),
            ("Hash", "@hash"),
            ("Author", "@author"),
            ("Message", "@message"),
            ("s", "@s2"),
            ("Number of samples", "@nsamples")
        ]

        plot.fill_dotplot(
            self.plots["s2_plot"], self.source, "s2",
            tooltips = s2_tooltips,
            js_tap_callback = js_tap_callback,
            server_tap_callback = self.inspect_run_callback,
            lines = True
        )
        s2_tab = Panel(child=self.plots["s2_plot"], title="Base 2")

        s_tabs = Tabs(
            name = "s_tabs",
            tabs=[s10_tab, s2_tab],
            tabs_location = "below"
        )

        self.doc.add_root(s_tabs)


    def setup_widgets(self):

            # Initial selections

        # Test/var/backend combination (we select all first elements at init)
        self.tests = self.data\
        .index.get_level_values("test").drop_duplicates().tolist()

        self.vars = self.data.loc[self.tests[0]]\
        .index.get_level_values("variable").drop_duplicates().tolist()

        self.backends = self.data.loc[self.tests[0], self.vars[0]]\
        .index.get_level_values("vfc_backend").drop_duplicates().tolist()


        # Custom JS callback that will be used client side to filter selections
        filter_callback_js = """
        selector.options = options.filter(e => e.includes(cb_obj.value));
        """


            # Test selector widget

        # Number of runs to display
        # The dict structure allows us to get int value from the display string
        # in O(1)
        self.n_runs_dict = {
            "Last 3 runs": 3,
            "Last 5 runs": 5,
            "Last 10 runs": 10,
            "All runs": 0
        }

        # Contains all options strings
        n_runs_display = list(self.n_runs_dict.keys())

        # Will be used when updating plots (contains actual number to diplay)
        self.current_n_runs = self.n_runs_dict[n_runs_display[1]]

        # Selector widget
        self.select_test = Select(
            name="select_test", title="Test :",
            value=self.tests[0], options=self.tests
        )
        self.doc.add_root(self.select_test)
        self.select_test.on_change("value", self.update_test)
        self.select_test.on_change("options", self.update_test)

        # Filter widget
        test_filter = TextInput(
            name="test_filter", title="Tests filter:"
        )
        test_filter.js_on_change("value", CustomJS(
            args=dict(options=self.tests, selector=self.select_test),
            code=filter_callback_js
        ))
        self.doc.add_root(test_filter)


            # Number of runs to display

        self.select_n_runs = Select(
            name="select_n_runs", title="Display :",
            value=n_runs_display[1], options=n_runs_display
        )
        self.doc.add_root(self.select_n_runs)
        self.select_n_runs.on_change("value", self.update_n_runs)


            # Variable selector widget

        self.select_var = Select(
            name="select_var", title="Variable :",
            value=self.vars[0], options=self.vars
        )
        self.doc.add_root(self.select_var)
        self.select_var.on_change("value", self.update_var)
        self.select_var.on_change("options", self.update_var)

        # BUG Since arguments to CustomJS are not updated, the filter might not
        # behave as expected after updating the tests (if tests don't have the
        # same variables). Until a solution is found, it is safer to remove this
        # filter from the report.
        # var_filter = TextInput(
        #     name="var_filter", title="Variables filter:"
        # )
        # var_filter.js_on_change("value", CustomJS(
        #     args=dict(options=self.vars, selector=self.select_var),
        #     code=filter_callback_js
        # ))
        # self.doc.add_root(var_filter)


            # Backend selector widget

        self.select_backend = Select(
            name="select_backend", title="Verificarlo backend :",
            value=self.backends[0], options=self.backends
        )
        self.doc.add_root(self.select_backend)
        self.select_backend.on_change("value", self.update_backend)



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

    def __init__(self, master, doc, data, metadata):

        self.master = master

        self.doc = doc
        self.data = data
        self.metadata = metadata

        # Will be filled/updated in update_plots()
        self.source = ColumnDataSource(data={})


        self.plots = {}

        # Setup Bokeh objects
        self.setup_plots()
        self.setup_widgets()


        # At this point, everything should have been initialized, so we can
        # show the plots for the first time
        self.update_plots()
