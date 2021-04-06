# Look for and read all the run files in the current directory (ending with
# .vfcrun.hd5), and lanch a Bokeh server for the visualization of this data.

import os
import datetime
import sys

import pandas as pd

from bokeh.plotting import figure, show, curdoc
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.models import Select, ColumnDataSource, Panel, Tabs, HoverTool, OpenURL, TapTool



################################################################################


    # Read vfcrun files, and aggregate them in one dataset

run_files = [ f for f in os.listdir(".") if f.endswith(".vfcrun.hd5") ]

if len(run_files) == 0:
    print("Could not find any vfcrun files in the directory. Exiting script.")
    exit(1)

# These are arrays of Pandas dataframes for now
metadata = []
data = []

for f in run_files:
    metadata.append(pd.read_hdf(f, "metadata"))
    data.append(pd.read_hdf(f, "data"))

metadata = pd.concat(metadata).sort_index()
data = pd.concat(data).sort_index()



################################################################################


    # Setup Bokeh server

curdoc().title = "Verificarlo Report"


    # Look for the Git repository remote address
    # (if a Git repo is specified, the webpage will contain hyperlinks to the
    # repository and the different commits)

git_repo_linked = False
commit_link = ""

if len(sys.argv) == 3:
    from urllib.parse import urlparse

    method = sys.argv[1]
    address = sys.argv[2]
    url = ""


    # Here, address is either the remote URL or the path to the local Git repo
    # (depending on the method)

    if method == "remote":
        # We should directly have a Git URL
        url = address

    elif method == "directory":
        # Fetch the remote URL from the local repo
        from git import Repo
        repo = Repo(address)
        url = repo.remotes.origin.url

    else:
        raise ValueError("The specified method to get the Git repository is "\
        "invalid. Are you calling Bokeh directly instead of using the "\
        "Verificarlo wrapper ?")


    # At this point, "url" should be set correctly, we can get the repo's
    # URL and name

    parsed_url = urlparse(url)

    path = parsed_url.path.split("/")
    if len(path) < 3:
        raise ValueError("The found URL doesn't seem to be pointing to a Git "\
        "repository (path is too short)")

    repo_name = path[2]

    curdoc().template_variables["repo_url"] = url
    curdoc().template_variables["repo_name"] = repo_name


    # We should have a "github.com" or a "*gitlab*" URL

    if parsed_url.netloc == "github.com":
        commit_link = "https://" + parsed_url.netloc + parsed_url.path + "/commit/@hash"
        curdoc().template_variables["commit_link"] = commit_link
        curdoc().template_variables["git_host"] = "GitHub"
        git_repo_linked = True

    elif "gitlab" in parsed_url.netloc:
        commit_link = "https://" + parsed_url.netloc + parsed_url.path + "/-/commit/@hash"
        curdoc().template_variables["git_host"] = "GitLab"
        git_repo_linked = True

    else:
        raise ValueError("The found URL doesn't seem to be a GitHub or GitLab URL")


curdoc().template_variables["git_repo_linked"] = git_repo_linked



    # Setup Bokeh interfaces

# Runs comparison
import compare_runs as cmp_runs

compare_runs = cmp_runs.CompareRuns(
    doc = curdoc(),
    data = data,
    metadata = metadata,
    git_repo_linked = git_repo_linked,
    commit_link = commit_link
)


# WIP Variables comparison
import compare_variables
compare_variables.doc = curdoc()
compare_variables.foo()
