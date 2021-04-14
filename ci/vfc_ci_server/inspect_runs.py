# Manage the view comparing the variables of a run

import datetime

import pandas as pd
import numpy as np

from math import pi

from bokeh.plotting import figure, show, curdoc
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.models import Select, ColumnDataSource, Panel, Tabs, HoverTool,\
TextInput, OpenURL, TapTool, Range, RadioButtonGroup, CustomJS

import helper

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


    # It's better to have one update_plots function for each mode since most of
    # the time we will likely update only one view

    # Update plots (variable selection mode only!)
    def update_var_plots(self):

        # For a given variable, get all backends (across all tests)
        backends = self.filtered_data[
            self.filtered_data.index.isin([self.select_var.value], level=1)
        ].groupby("vfc_backend")

        backends = backends.agg({
            "sigma": lambda x: x.tolist(),
            "s10": lambda x: x.tolist(),
            "s2": lambda x: x.tolist(),
            "mu": lambda x: x.tolist(),

            # Used for mu weighted average first, then will be replaced
            "nsamples": lambda x: x.tolist()
        })


        # From there, we can compute the sigma/s quantiles, as well as the
        # aggregated mu (with a weighted avg using nsamples)

        backends["mu"] = np.vectorize(np.average)(backends["mu"], weights=backends["nsamples"])

        # Now that aggregated mu has been computed, nsamples is the number of
        # aggregated tests (which is the number of samples for our new sigma
        # and s distributions)
        backends["nsamples"] = backends["nsamples"].apply(lambda x: len(x))

        # Get quantiles and mu for sigma, s10, s2
        for stat in ["sigma", "s10", "s2"]:
            backends[stat] = backends[stat].apply(np.sort)
            backends["%s_min" % stat] = backends[stat].apply(np.min)
            backends["%s_quantile25" % stat] = backends[stat].apply(np.quantile, args=(0.25,))
            backends["%s_quantile50" % stat] = backends[stat].apply(np.quantile, args=(0.50,))
            backends["%s_quantile75" % stat] = backends[stat].apply(np.quantile, args=(0.75,))
            backends["%s_max" % stat] = backends[stat].apply(np.max)
            backends["%s_mu" % stat] = backends[stat].apply(np.average)
            del backends[stat]

        backends["x"] = backends.index
        backends["x"] = backends["x"].apply(
            lambda x: x[:17] + "[...]" + x[-17:] if len(x) > 39 else x
        )
        self.var_source.data = backends.to_dict("list")

        # Update x_ranges
        self.mu_var.x_range.factors = list(backends["x"])
        self.sigma_var.x_range.factors = list(backends["x"])
        self.s10_var.x_range.factors = list(backends["x"])
        self.s2_var.x_range.factors = list(backends["x"])


    # Update plots (backend selection mode only!)
    def update_backend_plots(self):

        # For a given backend, get all variables (across all tests)
        vars = self.filtered_data[
            self.filtered_data.index.isin([self.select_backend.value], level=2)
        ].groupby("variable")

        vars = vars.agg({
            "sigma": lambda x: x.tolist(),
            "s10": lambda x: x.tolist(),
            "s2": lambda x: x.tolist(),
            "mu": lambda x: x.tolist(),

            # Used for mu weighted average first, then will be replaced
            "nsamples": lambda x: x.tolist()
        })

        # From there, we can compute the sigma/s quantiles, as well as the
        # aggregated mu (with a weighted avg using nsamples)

        vars["mu"] = np.vectorize(np.average)(vars["mu"], weights=vars["nsamples"])

        # Now that aggregated mu has been computed, nsamples is the number of
        # aggregated tests (which is the number of samples for our new sigma
        # and s distributions)
        vars["nsamples"] = vars["nsamples"].apply(lambda x: len(x))

        # Get quantiles and mu for sigma, s10, s2
        for stat in ["sigma", "s10", "s2"]:
            vars[stat] = vars[stat].apply(np.sort)
            vars["%s_min" % stat] = vars[stat].apply(np.min)
            vars["%s_quantile25" % stat] = vars[stat].apply(np.quantile, args=(0.25,))
            vars["%s_quantile50" % stat] = vars[stat].apply(np.quantile, args=(0.50,))
            vars["%s_quantile75" % stat] = vars[stat].apply(np.quantile, args=(0.75,))
            vars["%s_max" % stat] = vars[stat].apply(np.max)
            vars["%s_mu" % stat] = vars[stat].apply(np.average)
            del vars[stat]

        vars["x"] = vars.index
        self.backend_source.data = vars.to_dict("list")

        # Update x_ranges
        self.mu_backend.x_range.factors = list(vars["x"])
        self.sigma_backend.x_range.factors = list(vars["x"])
        self.s10_backend.x_range.factors = list(vars["x"])
        self.s2_backend.x_range.factors = list(vars["x"])



        # Plots generation function (fills an existing plot with data)

    def gen_boxplot(self, plot, source, prefix):
        # (based on: https://docs.bokeh.org/en/latest/docs/gallery/boxplot.html)

        hover = HoverTool(tooltips = [
            ("Min", "@" + prefix + "_min{%0.18e}"),
            ("Max", "@" + prefix + "_max{%0.18e}"),
            ("1st quartile", "@" + prefix + "_quantile25{%0.18e}"),
            ("Median", "@" + prefix + "_quantile50{%0.18e}"),
            ("3rd quartile", "@" + prefix + "_quantile75{%0.18e}"),
            ("μ", "@" + prefix + "_mu{%0.18e}"),
            ("Number of samples (tests)", "@nsamples")
        ])
        hover.formatters = {
            "@%s_min" % prefix : "printf",
            "@%s_max" % prefix : "printf",
            "@%s_quantile25" % prefix : "printf",
            "@%s_quantile50" % prefix : "printf",
            "@%s_quantile75" % prefix : "printf",
            "@%s_mu" % prefix : "printf"
        }
        plot.add_tools(hover)


        # Stems
        self.top_stem = plot.segment(
            x0="x", y0="%s_max" % prefix,
            x1="x", y1="%s_quantile75" % prefix,
            source=source, line_color="black"
        )
        bottom_stem = plot.segment(
            x0="x", y0="%s_min" % prefix,
            x1="x", y1="%s_quantile25" % prefix,
            source=source, line_color="black"
        )

        # Boxes
        top_box = plot.vbar(
            x="x", width=0.5,
            top="%s_quantile75" % prefix, bottom="%s_quantile50" % prefix,
            source=source, line_color="black"
        )
        bottom_box = plot.vbar(
            x="x", width=0.5,
            top="%s_quantile50" % prefix, bottom="%s_quantile25" % prefix,
            source=source, line_color="black"
        )


        # Mu dot
        mu_dot = plot.dot(
            x="x", y="%s_mu" % prefix, size=30, source=source,
            color="black", legend_label="Empirical average μ"
        )


        # Other
        plot.xgrid.grid_line_color = None
        plot.ygrid.grid_line_color = None

        plot.yaxis[0].formatter.power_limit_high = 0
        plot.yaxis[0].formatter.power_limit_low = 0
        plot.yaxis[0].formatter.precision = 3

        plot.xaxis[0].major_label_orientation = pi/8


    def gen_bar_plot(self, plot, source):
        # This is used for plotting the mu bar plot only

        hover = HoverTool(tooltips = [
            ("μ", "@mu{%0.18e}"),
            ("Number of samples (tests)", "@nsamples")
        ])
        hover.formatters = {
            "@mu" : "printf"
        }
        plot.add_tools(hover)


        bar = plot.vbar(
            x="x", top="mu", source=source,
            width=0.5
        )
        plot.xgrid.grid_line_color = None
        plot.ygrid.grid_line_color = None

        plot.yaxis[0].formatter.power_limit_high = 0
        plot.yaxis[0].formatter.power_limit_low = 0
        plot.yaxis[0].formatter.precision = 3

        plot.xaxis[0].major_label_orientation = pi/8



        # Widets' callback functions

    def update_run(self, attrname, old, new):

        # Update_run selection (both display and timestamp by using dict mapping)
        self.current_run_display = new
        self.current_run = self.runs_dict[new]

        # This will be reused when updating plots (to avoid filtering same data)
        self.filtered_data = self.data[self.data["timestamp"] == self.current_run]

        # New list of available vars
        self.vars = self.filtered_data.index.\
        get_level_values("variable").drop_duplicates().tolist()
        self.select_var.options = self.vars

        # Reset variable selection if old one is not available in new vars
        if self.select_var.value not in self.vars:
            self.select_var.value = self.vars[0]

        else:
            # We still need to redraw the var plots
            self.update_var_plots()


        # New list of available backends
        self.backends = self.filtered_data.index.\
        get_level_values("vfc_backend").drop_duplicates().tolist()
        self.select_backend.options = self.backends

        # Reset backend selection if old one is not available in new backends
        if self.select_backend.value not in self.backends:
            self.select_backend.value = self.backends[0]

        else:
            # We still need to redraw the backend plots
            self.update_backend_plots()




    def update_var(self, attrname, old, new):
        self.update_var_plots()


    def update_backend(self, attrname, old, new):
        self.update_backend_plots()



        # Setup functions

    # Setup all initial selections (for both variable and backend selection at once)
    def setup_selection(self):

        # Dict contains all inspectable runs (maps display strings to timestamps)
        # The dict structure allows to get the timestamp from the display string
        # in O(1)
        self.runs_dict = self.gen_runs_selection()

        # Contains all options strings
        self.runs_display = list(self.runs_dict.keys())

        # Will be used when updating plots (contains actual number)
        self.current_run = self.runs_dict[self.runs_display[-1]]

        # Contains the selected option string, used to update current_n_runs
        self.current_run_display = self.runs_display[-1]


        # Once a run is selected, it is possible to select either a variable
        # or a backend to obtain plots (via a radio button to switch modes)
        self.modes = ["Select a variable", "Select a backend"]
        self.current_mode = 0 # Variable is selected by default


        # This will be reused when updating plots (to avoid filtering same data)
        self.filtered_data = self.data[self.data["timestamp"] == self.current_run]

        # Variable selection
        self.vars = self.filtered_data.index.\
        get_level_values("variable").drop_duplicates().tolist()

        # Backend_selection
        self.backends = self.filtered_data.index.\
        get_level_values("vfc_backend").drop_duplicates().tolist()


    # Create all plots (for both variable and backend selection at once)
    def setup_plots(self):

        tools = "pan, wheel_zoom, xwheel_zoom, ywheel_zoom, reset, save"

            # Variable selection plots

        # Mu plot
        self.mu_var = figure(
            name="mu_var",
            title="Empirical average μ of variable (groupped by backends)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode="scale_width"
        )
        self.gen_bar_plot(self.mu_var, self.var_source)
        self.doc.add_root(self.mu_var)


        # Sigma plot (variable selection)
        self.sigma_var = figure(
            name="sigma_var",
            title="Standard deviation σ of variable (groupped by backends)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode="scale_width"
        )
        self.gen_boxplot(self.sigma_var, self.var_source, "sigma")
        self.doc.add_root(self.sigma_var)


        # s plots (variable selection)
        self.s10_var = figure(
            name="s10_var",
            title="Significant digits s of variable (groupped by backends)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode='scale_width'
        )
        self.gen_boxplot(self.s10_var, self.var_source, "s10")
        s10_tab_var = Panel(child=self.s10_var, title="Base 10")

        self.s2_var = figure(
            name="s2_var",
            title="Significant digits s of variable (groupped by backends)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode='scale_width'
        )
        self.gen_boxplot(self.s2_var, self.var_source, "s2")
        s2_tab_var = Panel(child=self.s2_var, title="Base 2")

        s_tabs_var = Tabs(
            name = "s_tabs_var", tabs=[s10_tab_var, s2_tab_var],
            tabs_location = "below"
        )
        self.doc.add_root(s_tabs_var)


            # Backend selection plots

        # Mu plot
        self.mu_backend = figure(
            name="mu_backend",
            title="Empirical average μ of backend (groupped by variables)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode="scale_width"
        )
        self.gen_bar_plot(self.mu_backend, self.backend_source)
        self.doc.add_root(self.mu_backend)


        # Sigma plot (backend selection)
        self.sigma_backend = figure(
            name="sigma_backend",
            title="Standard deviation σ of backend (groupped by variables)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode="scale_width"
        )
        self.gen_boxplot(self.sigma_backend, self.backend_source, "sigma")
        self.doc.add_root(self.sigma_backend)


        # s plots (backend selection)
        self.s10_backend = figure(
            name="s10_backend",
            title="Significant digits s of backend (groupped by variables)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode='scale_width'
        )
        self.gen_boxplot(self.s10_backend, self.backend_source, "s10")
        s10_tab_backend = Panel(child=self.s10_backend, title="Base 10")

        self.s2_backend = figure(
            name="s2_backend",
            title="Significant digits s of backend (groupped by variables)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode='scale_width'
        )
        self.gen_boxplot(self.s2_backend, self.backend_source, "s2")
        s2_tab_backend = Panel(child=self.s2_backend, title="Base 2")

        s_tabs_backend = Tabs(
            name = "s_tabs_backend",
            tabs=[s10_tab_backend, s2_tab_backend], tabs_location = "below"
        )
        self.doc.add_root(s_tabs_backend)




    # Create all widgets (for both variable and backend selection at once)
    def setup_widgets(self):

        # Run selection
        self.select_run = Select(
            name="select_run", title="Run :",
            value=self.current_run_display, options=self.runs_display
        )
        self.doc.add_root(self.select_run)
        self.select_run.on_change("value", self.update_run)


        # Plotting mode radio

        radio = RadioButtonGroup(
            name="radio",
            labels=self.modes, active=self.current_mode
        )
        # This is a function defined inside the template to avoid writing too
        # much JS server side
        radio_callback_js = "changePlottingMode();"
        radio.js_on_change("active", CustomJS(
            code=radio_callback_js
        ))
        self.doc.add_root(radio)


        # Variable selection (mode 0)
        self.select_var = Select(
            # We need a different name to avoid collision in the template with
            # the runs comparison's widget
            name="select_variable_by_run", title="Variable :",
            value=self.vars[0], options=self.vars
        )
        self.doc.add_root(self.select_var)
        self.select_var.on_change("value", self.update_var)

        # Backend selection (mode 1)
        self.select_backend = Select(
            # We need a different name to avoid collision in the template with
            # the runs comparison's widget
            name="select_backend_by_run", title="Backend :",
            value=self.backends[0], options=self.backends
        )
        self.doc.add_root(self.select_backend)
        self.select_backend.on_change("value", self.update_backend)



        # Communication methods
        # (to send/receive messages to/from master)

    # When received, switch to the run_name in parameter
    def switch_view(self, run_name):
        self.select_run.value = run_name

        # Simply call the run selector's callback function, as if the event had
        # been triggered manually
        self.update_run("", "", run_name)


        # Constructor

    def __init__(self, master, doc, data, metadata, git_repo_linked, commit_link):

        self.master = master

        self.doc = doc
        self.data = data
        self.metadata = metadata
        self.git_repo_linked = git_repo_linked
        self.commit_link = commit_link


        # Having 2 separate ColumnDataSource will prevent many useless
        # operations when updating one view only
        # (will be filled/updated in update_..._plots())
        self.var_source = ColumnDataSource(data={})
        self.backend_source = ColumnDataSource(data={})


        # Setup functions
        self.setup_selection()
        self.setup_plots()
        self.setup_widgets()


        # At this point, everything should have been initialized, so we can
        # show the plots for the first time
        self.update_var_plots()
        self.update_backend_plots()
