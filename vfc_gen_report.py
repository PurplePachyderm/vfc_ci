# Look for and read all the run files in the current directory (ending with
# .vfcrun.json). It will then generate a "report.html" file.

import os
import json

import numpy as np
import pandas as pd

from bokeh.plotting import figure, show
from bokeh.resources import INLINE
from bokeh.embed import components

from jinja2 import Environment, FileSystemLoader


# Look for all run files in current directory
run_files = [ f for f in os.listdir(".") if f.endswith(".vfcrun.json") ]


# Get the set of tests accross all runs


# For each test, generate the Bokeh plots


# Generate the template
