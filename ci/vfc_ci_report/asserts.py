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

from math import nan

import pandas as pd

from bokeh.embed import components
from bokeh.models import Select, ColumnDataSource, DataTable, TableColumn, \
    CustomJS

import helper

##########################################################################


class Asserts:

        # Asserts related helper

    def gen_source(self):

        # Combine data and deterministic data in a single source dataframe
        source_df = pd.concat([self.run_data, self.deterministic_run_data])
        source_df.reset_index(inplace=True)
        self.source.data = source_df

        # Widgets' callback functions

    def update_run(self, attrname, old, new):

        # Update run selection (by using dict mapping)
        self.current_run = self.runs_dict[new]

        # Update run data
        self.run_data = self.data[self.data["timestamp"] == self.current_run]
        self.deterministic_run_data = self.deterministic_data[
            self.deterministic_data["timestamp"] == self.current_run
        ]

        # Only keep interesting columns for both data and deterministic_data
        self.run_data = self.run_data[[
            "assert", "accuracy_threshold",
            "mu", "sigma",
        ]]

        self.deterministic_run_data = self.deterministic_run_data[[
            "assert", "accuracy_threshold",
            "value", "reference_value",
        ]]

        # Only keep probes that have an assert
        self.run_data = self.run_data[self.run_data.accuracy_threshold != 0]
        self.deterministic_run_data=self.deterministic_run_data[
            self.deterministic_run_data.accuracy_threshold != 0
        ]

        # Generate the main data source from the 2 filtered dataframes
        self.gen_source()

        # Bokeh setup functions
    def setup_widgets(self):

        # Run selection

        # Dict contains all inspectable runs (maps display strings to timestamps)
        # The dict structure allows to get the timestamp from the display string
        # in O(1)
        self.runs_dict= helper.gen_runs_selection(self.metadata)

        # Contains all options strings
        runs_display= list(self.runs_dict.keys())
        # Will be used when updating plots (contains actual number)
        self.current_run= self.runs_dict[runs_display[-1]]

        # Contains the selected option string, used to update current_n_runs
        current_run_display= runs_display[-1]

        # This contains only entries matching the run
        self.run_data= self.data[self.data["timestamp"] == self.current_run]
        self.deterministic_run_data = self.deterministic_data[
            self.deterministic_data["timestamp"] == self.current_run
        ]

        # Only keep interesting columns for both data and deterministic_data
        self.run_data = self.run_data[[
            "assert", "accuracy_threshold",
            "mu", "sigma",
        ]]

        self.deterministic_run_data = self.deterministic_run_data[[
            "assert", "accuracy_threshold",
            "value", "reference_value",
        ]]

        # Only keep probes that have an assert
        self.run_data = self.run_data[self.run_data.accuracy_threshold != 0]
        self.deterministic_run_data=self.deterministic_run_data[
            self.deterministic_run_data.accuracy_threshold != 0
        ]


        change_run_callback_js= "updateRunMetadata(cb_obj.value, \"asserts-\");"

        self.widgets["select_assert_run"] = Select(
            name = "select_assert_run", title = "Run :",
            value = current_run_display, options = runs_display
        )
        self.doc.add_root(self.widgets["select_assert_run"])
        self.widgets["select_assert_run"].on_change("value", self.update_run)
        self.widgets["select_assert_run"].js_on_change("value", CustomJS(
            code=change_run_callback_js,
            args=(dict(
                metadata=helper.metadata_to_dict(
                    helper.get_metadata(self.metadata, self.current_run)
                )
            ))
        ))

        # Main asserts table:

        columns=[
            TableColumn(field="test", title="Test"),
            TableColumn(field="variable", title="Variable"),
            TableColumn(field="vfc_backend", title="Backend"),
            TableColumn(field="accuracy_threshold", title="Target precision"),
            TableColumn(field="mu", title="μ (non-det.)"),
            TableColumn(field="sigma", title="σ (non-det.)"),
            TableColumn(field="value", title="Value (det.)"),
            TableColumn(field="reference_value", title="IEEE value (det.)"),
            TableColumn(field="assert", title="Passed"),
        ]

        self.widgets["asserts_table"]= DataTable(
            name = "asserts_table", source =self.source, columns=columns,
            width=895
        )
        self.doc.add_root(self.widgets["asserts_table"])


        # Communication methods
        # (to send/receive messages to/from master)

    def change_repo(self, new_data, new_deterministic_data, new_metadata):
        '''
        When received, update data and metadata with the new repo, and update
        everything
        '''

        self.data=new_data
        self.deterministic_data=new_deterministic_data
        self.metadata=new_metadata

        self.runs_dict=helper.gen_runs_selection(self.metadata)

        # Contains all options strings
        runs_display=list(self.runs_dict.keys())
        # Will be used when updating plots (contains actual number)
        self.current_run=self.runs_dict[runs_display[-1]]

        # Update run selection (this will automatically trigger the callback)

        self.widgets["select_assert_run"].options=runs_display

        # If the run name happens to be the same, the callback has to be
        # triggered manually
        if runs_display[-1] == self.widgets["select_assert_run"].value:
            update_run("value", runs_display[-1], runs_display[-1])

        # In any other case, updating the value is enough to trigger the
        # callback
        else:
            self.widgets["select_assert_run"].value=runs_display[-1]


    def switch_view(self, run_name):
        '''When received, switch selected run to run_name'''

        # This will trigger the widget's callback
        self.widgets["select_assert_run"].value = run_name


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

        self.master=master

        self.doc=doc
        self.data=data
        self.deterministic_data=deterministic_data
        self.metadata=metadata

        self.source=ColumnDataSource({})

        self.widgets={}

        # Setup Bokeh objects
        self.setup_widgets()

        # At this point, everything should have been initialized, so we can
        # show the data for the first time
        self.gen_source()
