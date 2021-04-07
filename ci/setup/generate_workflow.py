# Creates the .yml of the workflow running the tests on the dev branch

import sys
from jinja2 import Environment, FileSystemLoader


# Check arguments
if len(sys.argv) != 3:
	print("ERROR : Wrong number of arguments")
	print("Usage : python setup_report_workflow.py [dev branch name] [CI branch name]")
	exit(-1)


# Init template loader
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('vfc_test_workflow.j2.yml')


# Render templates
render = template.render(dev_branch=sys.argv[1], ci_branch=sys.argv[2])


# Write template
with open(".github/workflows/vfc_test_workflow.yml", "w") as fh:
    fh.write(render)
