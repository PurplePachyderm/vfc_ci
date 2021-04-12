# Manage the view comparing the variables of a run

import datetime

import pandas as pd

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
            str = helper.runs_tick_string(row.name, row["hash"])
            runs_dict[str] = row.name

        return runs_dict


    # It's better to have one update_plots function for each mode since most of
    # the time we will likely update only one view

    # Update plots (variable selection mode only!)
    def update_var_plots(self):
        print("Update var plots")


    # Update plots (backend selection mode only!)
    def update_backend_plots(self):
        print("Update backend plots")



        # Plots generation function



        # Widets' callback functions

    def update_run(self, attrname, old, new):

        # Update_run selection (both display and timestamp by using dict mapping)
        self.current_run_display = new
        self.current_run = self.runs_dict[new]

        filtered_data = self.data.loc[self.data["timestamp"] == self.current_run]

        self.vars = filtered_data.index.\
        get_level_values("variable").drop_duplicates().tolist()

        # Reset variable selection if old one is not available in new vars
        if self.current_var not in self.vars:
            self.current_var = self.vars[0]
            self.select_var.value = self.current_var


        self.backends = filtered_data.index.\
        get_level_values("vfc_backend").drop_duplicates().tolist()

        # Reset backend selection if old one is not available in new backends
        if self.current_backend not in self.backends:
            self.current_backend = self.backends[0]
            self.select_var.value = self.current_backend


        # This is the only operation that requires redrawing all plots
        self.update_var_plots()
        self.update_backend_plots()


    def update_var(self, attrname, old, new):
        self.current_var = new
        self.update_var_plots()


    def update_backend(self, attrname, old, new):
        self.current_backend = new
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


        filtered_data = self.data.loc[self.data["timestamp"] == self.current_run]

        # Variable selection
        self.vars = filtered_data.index.\
        get_level_values("variable").drop_duplicates().tolist()
        self.current_var = self.vars[0]

        # Backend_selection
        self.backends = filtered_data.index.\
        get_level_values("vfc_backend").drop_duplicates().tolist()
        self.current_backend = self.backends[0]


    # Create all plots (for both variable and backend selection at once)
    def setup_plots(self):

        tools = "pan, wheel_zoom, xwheel_zoom, ywheel_zoom, reset, save"

            # Variable selection plots

        # Sigma plot (variable selection)
        self.sigma_var = figure(
            name="sigma_var", title="Standard deviation σ of variable (groupped by backends)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode="scale_width"
        )
        # TODO Gen plot
        self.doc.add_root(self.sigma_var)


        # s plots (variable selection)
        self.s10_var = figure(
            name="s10_var",
            title="Significant digits s of variable (groupped by backends)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode='scale_width'
        )
        # TODO Gen plot
        s10_tab_var = Panel(child=self.s10_var, title="Base 10")

        self.s2_var = figure(
            name="s2_var",
            title="Significant digits s of variable (groupped by backends)",
            plot_width=900, plot_height=400, x_range=[""], y_range=(-2.5, 53),
            tools=tools, sizing_mode='scale_width'
        )
        # TODO Gen plot
        s2_tab_var = Panel(child=self.s2_var, title="Base 2")

        s_tabs_var = Tabs(
            name = "s_tabs_var", tabs=[s10_tab_var, s2_tab_var],
            tabs_location = "below"
        )
        self.doc.add_root(s_tabs_var)


            # Backend selection plots

        # Sigma plot (backend selection)
        self.sigma_backend = figure(
            name="sigma_backend",
            title="Standard deviation σ of backend (groupped by variables)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode="scale_width"
        )
        # TODO Gen plot
        self.doc.add_root(self.sigma_backend)


        # s plots (backend selection)
        self.s10_backend = figure(
            name="s10_backend",
            title="Significant digits s of backend (groupped by variables)",
            plot_width=900, plot_height=400, x_range=[""],
            tools=tools, sizing_mode='scale_width'
        )
        # TODO Gen plot
        s10_tab_backend = Panel(child=self.s10_backend, title="Base 10")

        self.s2_backend = figure(
            name="s2_backend", title="Significant digits s of backend (groupped by variables)",
            plot_width=900, plot_height=400, x_range=[""], y_range=(-2.5, 53),
            tools=tools, sizing_mode='scale_width'
        )
        # TODO Gen plot
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
            value=self.current_var, options=self.vars
        )
        self.doc.add_root(self.select_var)
        self.select_var.on_change("value", self.update_var)

        # Backend selection (mode 1)
        self.select_backend = Select(
            # We need a different name to avoid collision in the template with
            # the runs comparison's widget
            name="select_backend_by_run", title="Backend :",
            value=self.current_backend, options=self.backends
        )
        self.doc.add_root(self.select_backend)
        self.select_backend.on_change("value", self.update_backend)



        # Communication methods
        # (called from master to update this class from outside)


        # Constructor

    def __init__(self, master, doc, data, metadata, git_repo_linked, commit_link):

        self.master = master

        self.doc = doc
        self.data = data
        self.metadata = metadata
        self.git_repo_linked = git_repo_linked
        self.commit_link = commit_link

        # Having 2 separate sources will prevent many useless operations when
        # updating one view only
        # (will be filled/updated in update_..._plots())
        self.variable_source = ColumnDataSource(data={})
        self.backend_source = ColumnDataSource(data={})


        # Setup everything
        self.setup_selection()
        self.setup_plots()
        self.setup_widgets()


        # At this point, everything should have been initialized, so we can
        # show the plots for the first time
        self.update_var_plots()
        self.update_backend_plots()
