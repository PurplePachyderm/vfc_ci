# This file makes it possible to compare the different variables inside a single
# run

from bokeh.models import Select
from bokeh.plotting import curdoc


def foo():
    foo = Select(
        name="foo", title="bar",
        value="", options=["foo", "bar"]
    )
    doc.add_root(foo)
