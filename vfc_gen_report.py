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


    # Look for all run files in current directory and read them

print("Looking for run files...")

run_files = [ f for f in os.listdir(".") if f.endswith(".vfcrun.json") ]

runs = []
for f in run_files:
    with open(f, "r") as file:
        runs.append(json.loads(file.read()))


    # Organize the data by results

print("Re-arranging data...")

# Convert dictionary to Pandas dataframe for easier manipulation
runs = pd.DataFrame.from_dict(runs)

# Unroll by tests
runs = runs.explode("tests")
runs = pd.concat([runs.drop(["tests"], axis=1), runs["tests"].apply(pd.Series)], axis=1)

# Unroll by backend results
runs = runs.explode("results")
runs = pd.concat([runs.drop(["results"], axis=1), runs["results"].apply(pd.Series)], axis=1)

runs.rename(columns = {'name':'test'}, inplace = True)
runs = runs.reset_index(drop=True)

# At this point, each dataframe row represents a run for one test/backend combination,
# and has the following columns :
# timestamp, is_git_commit, commit_metadata, test, vfc_backend, values


    # Actual data processing (compute average, standard deviation, significant digits)

print("Processing data...")

def numpy_float_array(x):
    return np.array(x).astype(float)

def get_quantile(array, p):
    return np.quantile(array, p)

runs["values"] = runs["values"].apply(numpy_float_array)

runs["mu"] = runs["values"].apply(np.average)
runs["sigma"] = runs["values"].apply(np.std)

# NOTE : What about s when the sample's avg is 0 ? (divison by 0 returns NaN)
runs["s10"] = - np.log10(np.absolute( runs["sigma"] / runs["mu"] ))
runs["s2"] = - np.log2(np.absolute( runs["sigma"] / runs["mu"] ))

# NOTE : Would sorting runs["values"] before getting the quantiles give
# better performances ?
runs["quantile10"] = runs["values"].apply(get_quantile, args=(0.1,))
runs["quantile25"] = runs["values"].apply(get_quantile, args=(0.25,))
runs["quantile50"] = runs["values"].apply(get_quantile, args=(0.5,))
runs["quantile75"] = runs["values"].apply(get_quantile, args=(0.75,))
runs["quantile90"] = runs["values"].apply(get_quantile, args=(0.9,))

runs["values"] = runs["values"].tolist()


    # Group the runs by test then backend to get a hierarchical data structure
    # (in a dictionary)

# Group by test and convert to a dictionary
runs = dict(tuple(runs.groupby('test')))

for key, value in runs.items():
    # "test" column is now useless
    del value["test"]

    # Group by backends
    value = dict(tuple(value.groupby("vfc_backend")))

    for key2, value2 in value.items():
        print("Quartiles for array :")
        print(value2["quantile10"])
        print(value2["quantile25"])
        print(value2["quantile50"])
        print(value2["quantile75"])
        print(value2["quantile90"])

        # "vfc_backend" column is now useless
        del value2["vfc_backend"]


        # Convert last dataframes to list of dictionaries (and keep records names)
        value2 = value2.to_dict("records")

        # Convert all numpy arrays to lists
        for e in value2:
            e["values"] = e["values"].tolist()


        # Apply changes
        value[key2] = value2

    # Apply changes
    runs[key] = value

print(json.dumps(runs, indent=4))


    # Generate the Bokeh plots

print("[TODO] Generating plots...")

# Dummy Bokeh plot
# x = [1, 2, 3, 4, 5]
# y = [6, 7, 2, 4, 5]
# # create a new plot with a title and axis labels
# p1 = figure(title="Simple line example", x_axis_label="x", y_axis_label="y")
# # add a line renderer with legend and line thickness
# p1.line(x, y, legend_label="Temp.", line_width=2)

# Generate the mu plot for an array of results (of one test/backend combination)
def gen_mu_plot(results):
    commit_array = []   # Contains commit hash ?
    mu_array = []

    for e in results:
        commit_array.append(e["commit_metadata"]["hash"])
        mu_array.append(e["mu"])

    print(commit_array)
    print(mu_array)

    p = figure(title="Mu plot", x_axis_label='Commit', y_axis_label='\mu')
    p.line(commit_array, mu_array, line_color="blue", line_width=2)

    return p

p = gen_mu_plot(runs["Simple C test"]["libinterflop_mca.so --precision-binary64=24"])


    # Render Jinja2 template

print("[TODO] Rendering report file...")

env = Environment(loader=FileSystemLoader("."))
template = env.get_template("report.j2")

bokeh_js = INLINE.render_js()
bokeh_css = INLINE.render_css()

plots = {
    'plot1': p
}
bokeh_script, plots = components(plots)

render = template.render(arg="world",
                         bokeh_js=bokeh_js,
                         bokeh_css=bokeh_css,
                         bokeh_script=bokeh_script,
                         plots=plots)


    # Write file

with open("report.html", "w") as fh:
    fh.write(render)


    # Print termination message

print()
print('The report has been succesfully written in the "report.html" file.')
