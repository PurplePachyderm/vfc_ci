# Manage the view comparing the variables of a run

import datetime

import pandas as pd

from math import pi

from bokeh.plotting import figure, show, curdoc
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.models import Select, ColumnDataSource, Panel, Tabs, HoverTool,\
TextInput, OpenURL, TapTool, CustomJS, Range, RadioButtonGroup

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


    # Update plots based on current_test/var/backend combination
    def update_plots(self):
        # TODO
        return


        # Plots generation function



        # Widets' callback functions



        # Setup functions

    # Setup all initial selections (and possible selections)
    def setup_selection(self):

        # Dict contains all inspectable runs
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
        # or a backend to obtain plots (via a radio button)
        self.modes = ["Select a variable", "Select a backend"]
        self.current_mode = 0 # Variable is selected by default


        filtered_data = self.data.loc[self.data["timestamp"] == self.current_run]

        # Variable selection
        self.variables = filtered_data.index.\
        get_level_values("variable").drop_duplicates().tolist()

        # Backend_selection
        self.backends = filtered_data.index.\
        get_level_values("vfc_backend").drop_duplicates().tolist()



    # Create all plots
    def setup_plots(self):
        # TODO
        return


    # Create all widgets
    def setup_widgets(self):

        # Run selection
        self.select_run = Select(
            name="select_run", title="Current run :",
            value=self.current_run_display, options=self.runs_display
        )
        self.doc.add_root(self.select_run)
        # TODO Add callback


        # Plotting mode
        radio_callback_js = """
        // This is a function defined inside the template to avoid writing too
        // much JS server side
        changePlottingMode();
        """

        self.select_mode = RadioButtonGroup(
            name="select_mode",
            labels=self.modes, active=self.current_mode
        )
        # TODO Add callback (server side)

        # BUG Adding JS callbacks from 2 different files (probably from 2
        # different CustomJS imports, actually) causes a crash client side
        # self.select_mode.js_on_change("value", CustomJS(
        #     code=radio_callback_js
        # ))
        self.doc.add_root(self.select_mode)


        # Variable selection (mode 0)
        self.select_variable = Select(
            # We need a different name to avoid collision in the template with
            # the runs comparison's widget
            name="select_variable_by_run", title="Variable :",
            value=self.current_run_display, options=self.variables
        )
        self.doc.add_root(self.select_variable)
        # TODO Add callback

        # Backend selection (mode 1)
        self.select_backend = Select(
            # We need a different name to avoid collision in the template with
            # the runs comparison's widget
            name="select_backend_by_run", title="Backend :",
            value=self.current_run_display, options=self.backends
        )
        self.doc.add_root(self.select_backend)
        # TODO Add callback


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


        # At this point, everything should have been initialized, so we can
        # show the plots for the first time
        self.update_plots()
