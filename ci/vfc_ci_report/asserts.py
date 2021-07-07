#############################################################################
#                                                                           #
#  This file is part of Verificarlo.                                        #
#                                                                           #
#  Copyright (c) 2015-2021                                                  #
#     Verificarlo contributors                                              #
#     Universite de Versailles St-Quentin-en-Yvelines                       #
#     CMLA, Ecole Normale Superieure de Cachan                              #
#                                                                           #
#  Verificarlo is free software: you can redistribute it and/or modify      #
#  it under the terms of the GNU General Public License as published by     #
#  the Free Software Foundation, either version 3 of the License, or        #
#  (at your option) any later version.                                      #
#                                                                           #
#  Verificarlo is distributed in the hope that it will be useful,           #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#  GNU General Public License for more details.                             #
#                                                                           #
#  You should have received a copy of the GNU General Public License        #
#  along with Verificarlo.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                           #
#############################################################################

# Manage the view comparing the asserts by run.
# At its creation, a Asserts object will create all the needed Bokeh widgets,
# setup the callback functions (either server side or client side),
# initialize widgets selection, and from this selection generate the first plots.
# Then, when callback functions are triggered, widgets selections are updated,
# and re-generated with the newly selected data.

from bokeh.embed import components
from bokeh.models import Select, ColumnDataSource, CustomJS

import helper

##########################################################################


class Asserts:

        # Widgets' callback functions

    def update_table(self, attrname, old, new):
        print("[TODO] Update asserts table")

        # Bokeh setup functions
    def setup_widgets(self):

        # Run selection

        print("Asserts widgets setup")

        # Dict contains all inspectable runs (maps display strings to timestamps)
        # The dict structure allows to get the timestamp from the display string
        # in O(1)
        self.runs_dict = helper.gen_runs_selection(self.metadata)

        # Contains all options strings
        runs_display = list(self.runs_dict.keys())
        # Will be used when updating plots (contains actual number)
        self.current_run = self.runs_dict[runs_display[-1]]

        # Contains the selected option string, used to update current_n_runs
        current_run_display = runs_display[-1]

        # This contains only entries matching the run
        self.run_data = self.data[self.data["timestamp"] == self.current_run]
        self.deterministic_run_data = self.deterministic_data[self.deterministic_data["timestamp"] == self.current_run]

        change_run_callback_js = "updateRunMetadata(\"TODO\");"

        self.widgets["select_assert_run"] = Select(
            name="select_assert_run", title="Run :",
            value=current_run_display, options=runs_display
        )
        self.doc.add_root(self.widgets["select_assert_run"])
        self.widgets["select_assert_run"].on_change("value", self.update_table)
        self.widgets["select_assert_run"].js_on_change("value", CustomJS(
            code=change_run_callback_js,
            args=(dict(
                metadata=helper.metadata_to_dict(
                    helper.get_metadata(self.metadata, self.current_run)
                )
            ))
        ))

        # Communication methods
        # (to send/receive messages to/from master)

        # Constructor

    def __init__(self, master, doc, data, deterministic_data, metadata):
        '''
        Here are the most important attributes of the CompareRuns class

        master : reference to the ViewMaster class
        doc : an object provided by Bokeh to add elements to the HTML document
        data : pandas dataframe containing tests data (non-deterministic
        backends only)
        deterministic_data : pandas dataframe containing tests data (deterministic
        backends only)
        metadata : pandas dataframe containing all the tests metadata

        sources : ColumnDataSource object provided by Bokeh, contains current
        data (inside the .data attribute)
        widgets : dictionary of Bokeh widgets (no plots for this view)
        '''

        self.master = master

        self.doc = doc
        self.data = data
        self.deterministic_data = deterministic_data
        self.metadata = metadata

        self.sources = {}

        self.widgets = {}

        # Setup Bokeh objects
        self.setup_widgets()

        # At this point, everything should have been initialized, so we can
        # show the table for the first time
        self.update_table(0, 0, 0)
