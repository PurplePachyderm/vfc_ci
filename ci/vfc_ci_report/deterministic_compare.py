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

# Manage the view comparing results of deerministic backends over runs.
# At its creation, a DeterministicCompare object will create all the needed
# Bokeh widgets and plots, setup the callback functions (either server side or
# client side), initialize widgets selection, and from this selection generate
# the first plots. Then, when callback functions are triggered, widgets
# selections are updated, and plots are re-generated with the newly selected
# data.

import pandas as pd

from bokeh.plotting import figure, curdoc
from bokeh.embed import components
from bokeh.models import Select, ColumnDataSource


##########################################################################


class DeterministicCompare:

    # Plots update function

    def update_plots(self):
        return

        # Bokeh setup functions

    def setup_plots(self):
        return

    def setup_widgets(self):
        return

    # Constructor

    def __init__(self, master, doc, data, metadata):
        '''
        Here are the most important attributes of the CompareRuns class

        master : reference to the ViewMaster class
        doc : an object provided by Bokeh to add elements to the HTML document
        data : pandas dataframe containing all the tests data (only for
        deterministic backends)
        metadata : pandas dataframe containing all the tests metadata

        sources : ColumnDataSource object provided by Bokeh, contains current
        data for the plots (inside the .data attribute)
        plots : dictionary of Bokeh plots
        widgets : dictionary of Bokeh widgets
        '''

        self.master = master

        self.doc = doc
        self.data = data
        self.metadata = metadata

        self.sources = {}

        self.plots = {}
        self.widgets = {}

        # Setup Bokeh objects
        self.setup_plots()
        self.setup_widgets()

        # At this point, everything should have been initialized, so we can
        # show the plots for the first time
        self.update_plots()
