# Manage the view comparing the variables of a run

import json

import pandas as pd
import numpy as np


from math import pi
from bokeh.plotting import figure, curdoc
from bokeh.embed import components
from bokeh.models import Select, ColumnDataSource, Panel, Tabs, HoverTool,\
RadioButtonGroup, CustomJS

import helper
import plot

################################################################################



class InspectRuns:

        # Helper functions related to InspectRun

    # Returns a dictionary mapping user-readable strings to all run timestamps
    def gen_runs_selection(self):

        runs_dict = {}

        # Iterate over timestamp rows (runs) and fill dict
        for row in self.metadata.iloc:
            # The syntax used by pandas makes this part a bit tricky :
            # row.name is the index of metadata (so it refers to the
            # timestamp), whereas row["name"] is the column called "name"
            # (which is the display string used for the run)

            # runs_dict[run's name] = run's timestamp
            runs_dict[row["name"]] = row.name

        return runs_dict


    def gen_boxplot_tooltips(self, prefix):
        return [
            ("Name", "@x"),
            ("Min", "@" + prefix + "_min{%0.18e}"),
            ("Max", "@" + prefix + "_max{%0.18e}"),
            ("1st quartile", "@" + prefix + "_quantile25{%0.18e}"),
            ("Median", "@" + prefix + "_quantile50{%0.18e}"),
            ("3rd quartile", "@" + prefix + "_quantile75{%0.18e}"),
            ("μ", "@" + prefix + "_mu{%0.18e}"),
            ("Number of samples (tests)", "@nsamples")
        ]

    def gen_boxplot_tooltips_formatters(self, prefix):
        return {
            "@%s_min" % prefix : "printf",
            "@%s_max" % prefix : "printf",
            "@%s_quantile25" % prefix : "printf",
            "@%s_quantile50" % prefix : "printf",
            "@%s_quantile75" % prefix : "printf",
            "@%s_mu" % prefix : "printf"
        }


    # Data processing for all modes
    def data_processing(self, dataframe):

        dataframe["mu"] = np.vectorize(np.average)(dataframe["mu"], weights=dataframe["nsamples"])

        # Now that aggregated mu has been computed, nsamples is the number of
        # aggregated tests (which is the number of samples for our new sigma
        # and s distributions)
        dataframe["nsamples"] = dataframe["nsamples"].apply(lambda x: len(x))

        # Get quantiles and mu for sigma, s10, s2
        for stat in ["sigma", "s10", "s2"]:
            dataframe[stat] = dataframe[stat].apply(np.sort)
            dataframe["%s_min" % stat] = dataframe[stat].apply(np.min)
            dataframe["%s_quantile25" % stat] = dataframe[stat].apply(np.quantile, args=(0.25,))
            dataframe["%s_quantile50" % stat] = dataframe[stat].apply(np.quantile, args=(0.50,))
            dataframe["%s_quantile75" % stat] = dataframe[stat].apply(np.quantile, args=(0.75,))
            dataframe["%s_max" % stat] = dataframe[stat].apply(np.max)
            dataframe["%s_mu" % stat] = dataframe[stat].apply(np.average)
            del dataframe[stat]

        dataframe["x"] = dataframe.index
        dataframe["x"] = dataframe["x"].apply(
            lambda x: x[:17] + "[...]" + x[-17:] if len(x) > 39 else x
        )

        return dataframe


    # It's better to have one update_plots function for each mode since most of
    # the time we will likely update only one view

    # Update plots ("Group by backends" mode only)
    def update_backend_plots(self):

        # For a given variable, get all backends (across all tests)
        backends = self.filtered_data[
            self.filtered_data.index.isin([self.select_var_by_backend.value], level=1)
        ].groupby("vfc_backend")

        backends = backends.agg({
            "sigma": lambda x: x.tolist(),
            "s10": lambda x: x.tolist(),
            "s2": lambda x: x.tolist(),
            "mu": lambda x: x.tolist(),

            # Used for mu weighted average first, then will be replaced
            "nsamples": lambda x: x.tolist()
        })

        backends = self.data_processing(backends)

        self.backend_source.data = backends.to_dict("list")

        # Update x_ranges
        self.backend_plots["mu_backend"].x_range.factors = list(backends["x"])
        self.backend_plots["sigma_backend"].x_range.factors = list(backends["x"])
        self.backend_plots["s10_backend"].x_range.factors = list(backends["x"])
        self.backend_plots["s2_backend"].x_range.factors = list(backends["x"])

        helper.reset_x_ranges(self.backend_plots, list(backends["x"]))


    # Update plots ("Group by variables" mode only)
    def update_var_plots(self):

        # For a given backend, get all variables (across all tests)
        vars = self.filtered_data[
            self.filtered_data.index.isin([self.select_backend_by_var.value], level=2)
        ].groupby("variable")

        vars = vars.agg({
            "sigma": lambda x: x.tolist(),
            "s10": lambda x: x.tolist(),
            "s2": lambda x: x.tolist(),
            "mu": lambda x: x.tolist(),

            # Used for mu weighted average first, then will be replaced
            "nsamples": lambda x: x.tolist()
        })

        vars = self.data_processing(vars)

        self.var_source.data = vars.to_dict("list")

        # Update x_ranges
        helper.reset_x_ranges(self.var_plots, list(vars["x"]))


    # Update plots ("Group by tests" mode only)
    def update_test_plots(self):

        # For a given backend, get all tests (across all variables)
        tests = self.filtered_data[
            self.filtered_data.index.isin([self.select_backend_by_test.value], level=2)
        ].groupby("test")

        tests = tests.agg({
            "sigma": lambda x: x.tolist(),
            "s10": lambda x: x.tolist(),
            "s2": lambda x: x.tolist(),
            "mu": lambda x: x.tolist(),

            # Used for mu weighted average first, then will be replaced
            "nsamples": lambda x: x.tolist()
        })

        tests = self.data_processing(tests)

        self.test_source.data = tests.to_dict("list")

        # Update x_ranges
        helper.reset_x_ranges(self.test_plots, list(tests["x"]))



        # Widets' callback functions

    def update_run(self, attrname, old, new):

        # Update_run selection (both display and timestamp by using dict mapping)
        self.current_run_display = new
        self.current_run = self.runs_dict[new]

        # This will be reused when updating plots (to avoid filtering same data)
        self.filtered_data = self.data[self.data["timestamp"] == self.current_run]


        # New list of available vars
        vars = self.filtered_data.index.\
        get_level_values("variable").drop_duplicates().tolist()
        self.select_var_by_backend.options = vars

        # Reset variable selection if old one is not available in new vars
        if self.select_var_by_backend.value not in vars:
            self.select_var_by_backend.value = vars[0]

        else:
            # We still need to redraw the var plots
            self.update_var_plots()


        # New list of available backends
        backends = self.filtered_data.index.\
        get_level_values("vfc_backend").drop_duplicates().tolist()
        self.select_backend_by_var.options = backends

        # Reset backend selection if old one is not available in new backends
        if self.select_backend_by_var.value not in backends:
            self.select_backend_by_var.value = backends[0]
        else:
            # We still need to redraw the backend plots
            self.update_backend_plots()

        if self.select_backend_by_test.value not in backends:
            self.select_backend_by_test.value = backends[0]
        else:
            # We still need to redraw the backend plots
            self.update_test_plots()


    def update_var(self, attrname, old, new):
        self.update_var_plots()

    def update_backend(self, attrname, old, new):
        self.update_backend_plots()

    def update_test(self, attrname, old, new):
        self.update_test_plots()



        # Bokeh setup functions
        # (for both variable and backend selection at once)

    def setup_plots(self):

        tools = "pan, wheel_zoom, xwheel_zoom, ywheel_zoom, reset, save"


            # Tooltips and formatters

        dotplots_tooltips = [
            ("Name", "@x"),
            ("μ", "@mu{%0.18e}"),
            ("Number of samples (tests)", "@nsamples")
        ]
        dotplot_formatters = {
            "@mu" : "printf"
        }

        sigma_boxplot_tooltips = self.gen_boxplot_tooltips("sigma")
        sigma_boxplot_tooltips_formatters = self.gen_boxplot_tooltips_formatters("sigma")

        s10_boxplot_tooltips = self.gen_boxplot_tooltips("s10")
        s10_boxplot_tooltips_formatters = self.gen_boxplot_tooltips_formatters("s10")

        s2_boxplot_tooltips = self.gen_boxplot_tooltips("s2")
        s2_boxplot_tooltips_formatters = self.gen_boxplot_tooltips_formatters("s2")

            # "Group by backends" plots

        # Mu plot
        self.backend_plots["mu_backend"] = figure(
            name="mu_backend",
            title="Empirical average μ of variable (groupped by backends)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode="scale_width"
        )
        plot.fill_dotplot(
            self.backend_plots["mu_backend"], self.backend_source, "mu",
            tooltips = dotplots_tooltips,
            tooltips_formatters = dotplot_formatters
        )
        self.doc.add_root(self.backend_plots["mu_backend"])


        # Sigma plot
        self.backend_plots["sigma_backend"] = figure(
            name="sigma_backend",
            title="Standard deviation σ of variable (groupped by backends)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode="scale_width"
        )
        plot.fill_boxplot(
            self.backend_plots["sigma_backend"], self.backend_source, prefix="sigma",
            tooltips = sigma_boxplot_tooltips,
            tooltips_formatters = sigma_boxplot_tooltips_formatters
        )
        self.doc.add_root(self.backend_plots["sigma_backend"])


        # s plots
        self.backend_plots["s10_backend"] = figure(
            name="s10_backend",
            title="Significant digits s of variable (groupped by backends)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode='scale_width'
        )
        plot.fill_boxplot(
            self.backend_plots["s10_backend"], self.backend_source, prefix="s10",
            tooltips = s10_boxplot_tooltips,
            tooltips_formatters = s10_boxplot_tooltips_formatters
        )
        s10_tab_backend = Panel(child=self.backend_plots["s10_backend"], title="Base 10")

        self.backend_plots["s2_backend"] = figure(
            name="s2_backend",
            title="Significant digits s of variable (groupped by backends)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode='scale_width'
        )
        plot.fill_boxplot(
            self.backend_plots["s2_backend"], self.backend_source, prefix="s2",
            tooltips = s2_boxplot_tooltips,
            tooltips_formatters = s2_boxplot_tooltips_formatters
        )
        s2_tab_backend = Panel(child=self.backend_plots["s2_backend"], title="Base 2")

        s_tabs_backend = Tabs(
            name = "s_tabs_backend",
            tabs=[s10_tab_backend, s2_tab_backend], tabs_location = "below"
        )
        self.doc.add_root(s_tabs_backend)



            # "Group by variables" plots

        # Mu plot
        self.var_plots["mu_var"] = figure(
            name="mu_var",
            title="Empirical average μ of backend (groupped by variables)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode="scale_width"
        )
        plot.fill_dotplot(
            self.var_plots["mu_var"], self.var_source, "mu",
            tooltips = dotplots_tooltips,
            tooltips_formatters = dotplot_formatters
        )
        self.doc.add_root(self.var_plots["mu_var"])


        # Sigma plot
        self.var_plots["sigma_var"] = figure(
            name="sigma_var",
            title="Standard deviation σ of backend (groupped by variables)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode="scale_width"
        )
        plot.fill_boxplot(
            self.var_plots["sigma_var"], self.var_source, prefix="sigma",
            tooltips = sigma_boxplot_tooltips,
            tooltips_formatters = sigma_boxplot_tooltips_formatters
        )
        self.doc.add_root(self.var_plots["sigma_var"])


        # s plots
        self.var_plots["s10_var"] = figure(
            name="s10_var",
            title="Significant digits s of backend (groupped by variables)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode='scale_width'
        )
        plot.fill_boxplot(
            self.var_plots["s10_var"], self.var_source, prefix="s10",
            tooltips = s10_boxplot_tooltips,
            tooltips_formatters = s10_boxplot_tooltips_formatters
        )
        s10_tab_var = Panel(child=self.var_plots["s10_var"], title="Base 10")

        self.var_plots["s2_var"] = figure(
            name="s2_var",
            title="Significant digits s of backend (groupped by variables)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode='scale_width'
        )
        plot.fill_boxplot(
            self.var_plots["s2_var"], self.var_source, prefix="s2",
            tooltips = s2_boxplot_tooltips,
            tooltips_formatters = s2_boxplot_tooltips_formatters
        )
        s2_tab_var = Panel(child=self.var_plots["s2_var"], title="Base 2")

        s_tabs_var = Tabs(
            name = "s_tabs_var", tabs=[s10_tab_var, s2_tab_var],
            tabs_location = "below"
        )
        self.doc.add_root(s_tabs_var)



            # "Group by tests" plots

        # Mu plot
        self.test_plots["mu_test"] = figure(
            name="mu_test",
            title="Empirical average μ of backend (groupped by variables)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode="scale_width"
        )
        plot.fill_dotplot(
            self.test_plots["mu_test"], self.test_source, "mu",
            tooltips = dotplots_tooltips,
            tooltips_formatters = dotplot_formatters
        )
        self.doc.add_root(self.test_plots["mu_test"])


        # Sigma plot
        self.test_plots["sigma_test"] = figure(
            name="sigma_test",
            title="Standard deviation σ of backend (groupped by variables)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode="scale_width"
        )
        plot.fill_boxplot(
            self.test_plots["sigma_test"], self.test_source, prefix="sigma",
            tooltips = sigma_boxplot_tooltips,
            tooltips_formatters = sigma_boxplot_tooltips_formatters
        )
        self.doc.add_root(self.test_plots["sigma_test"])


        # s plots
        self.test_plots["s10_test"] = figure(
            name="s10_test",
            title="Significant digits s of backend (groupped by variables)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode='scale_width'
        )
        plot.fill_boxplot(
            self.test_plots["s10_test"], self.test_source, prefix="s10",
            tooltips = s10_boxplot_tooltips,
            tooltips_formatters = s10_boxplot_tooltips_formatters
        )
        s10_tab_test = Panel(child=self.test_plots["s10_test"], title="Base 10")

        self.test_plots["s2_test"] = figure(
            name="s2_test",
            title="Significant digits s of backend (groupped by variables)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode='scale_width'
        )
        plot.fill_boxplot(
            self.test_plots["s2_test"], self.test_source, prefix="s2",
            tooltips = s2_boxplot_tooltips,
            tooltips_formatters = s2_boxplot_tooltips_formatters
        )
        s2_tab_test = Panel(child=self.test_plots["s2_test"], title="Base 2")

        s_tabs_test = Tabs(
            name = "s_tabs_test", tabs=[s10_tab_test, s2_tab_test],
            tabs_location = "below"
        )
        self.doc.add_root(s_tabs_test)


    def setup_widgets(self):

            # Run selection

        # Dict contains all inspectable runs (maps display strings to timestamps)
        # The dict structure allows to get the timestamp from the display string
        # in O(1)
        self.runs_dict = self.gen_runs_selection()

        # Contains all options strings
        runs_display = list(self.runs_dict.keys())

        # Will be used when updating plots (contains actual number)
        self.current_run = self.runs_dict[runs_display[-1]]

        # Contains the selected option string, used to update current_n_runs
        self.current_run_display = runs_display[-1]


        change_run_callback_js="updateRunMetadata(cb_obj.value);"

        self.select_run = Select(
            name="select_run", title="Run :",
            value=self.current_run_display, options=runs_display
        )
        self.doc.add_root(self.select_run)
        self.select_run.on_change("value", self.update_run)
        self.select_run.js_on_change("value", CustomJS(
            code = change_run_callback_js,
            args=(dict(
                metadata=helper.metadata_to_dict(
                    helper.get_metadata(self.metadata, self.current_run)
                )
            ))
        ))


            # Plotting mode radio

        # Once a run is selected, it is possible to group either by backend
        # or variable to obtain plots (via a radio button to switch modes)
        modes = ["Backends", "Variables", "Tests"]

        radio = RadioButtonGroup(
            name="radio",
            labels=modes, active=0
        )
        self.doc.add_root(radio)
        # The functions are defined inside the template to avoid writing too
        # much JS server side
        radio_callback_js = "changePlottingMode(cb_obj.active);"
        radio.js_on_change("active", CustomJS(code=radio_callback_js))


        # This will be reused when updating plots (to avoid filtering same data)
        self.filtered_data = self.data[self.data["timestamp"] == self.current_run]


            # Group by backends (mode 0)
            # (and select a variable)

        vars = self.filtered_data.index.\
        get_level_values("variable").drop_duplicates().tolist()

        self.select_var_by_backend = Select(
            # We need a different name to avoid collision in the template with
            # the runs comparison's widget
            name="select_var_by_backend", title="Select a variable :",
            value=vars[0], options=vars
        )
        self.doc.add_root(self.select_var_by_backend)
        self.select_var_by_backend.on_change("value", self.update_backend)


            # Group by variables (mode 1)
            # (and select a backend)

        backends = self.filtered_data.index.\
        get_level_values("vfc_backend").drop_duplicates().tolist()

        self.select_backend_by_var = Select(
            # We need a different name to avoid collision in the template with
            # the runs comparison's widget
            name="select_backend_by_var", title="Select a backend :",
            value=backends[0], options=backends
        )
        self.doc.add_root(self.select_backend_by_var)
        self.select_backend_by_var.on_change("value", self.update_var)


            # Group by tests (mode 2)
            # (and select a backend)

        self.select_backend_by_test = Select(
            # We need a different name to avoid collision in the template with
            # the runs comparison's widget
            name="select_backend_by_test", title="Select a backend :",
            value=backends[0], options=backends
        )
        self.doc.add_root(self.select_backend_by_test)
        self.select_backend_by_test.on_change("value", self.update_test)



        # Communication methods
        # (to send/receive messages to/from master)

    # When received, switch to the run_name in parameter
    def switch_view(self, run_name):
        self.select_run.value = run_name



        # Constructor

    def __init__(self, master, doc, data, metadata):

        self.master = master

        self.doc = doc
        self.data = data
        self.metadata = metadata


        # Having separate ColumnDataSources will prevent many useless
        # operations when updating only one view
        # (will be filled/updated in update_..._plots())
        self.backend_source = ColumnDataSource(data={})
        self.var_source = ColumnDataSource(data={})
        self.test_source = ColumnDataSource(data={})

        self.backend_plots = {}
        self.var_plots = {}
        self.test_plots = {}

        # Setup Bokeh objects
        self.setup_plots()
        self.setup_widgets()


        # At this point, everything should have been initialized, so we can
        # show the plots for the first time
        self.update_backend_plots()
        self.update_var_plots()
        self.update_test_plots()


        # Pass the initial metadata to the template (will be updated in CustomJS
        # callbacks). This is required because metadata is not displayed in a
        # Bokeh widget, so we can't update this with a server callback.
        initial_run = helper.get_metadata(self.metadata, self.current_run)
        self.doc.template_variables["initial_timestamp"] = self.current_run
