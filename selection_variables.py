from bokeh.models import ColumnDataSource

metadata = []
data = []

tests = []
current_test = ""

vars = []
current_var = ""

backends = []
current_backend = ""

# Number of runs to display
n_runs = {
    "Last 3 runs": 3,
    "Last 5 runs": 5,
    "Last 10 runs": 10,
    "All runs": 0
}
n_runs_display = list(n_runs.keys())

current_n_runs = n_runs[n_runs_display[1]]
current_n_runs_display = n_runs_display[1]

git_repo_linked = False
commit_link = ""

runs_source = ColumnDataSource(data={})
