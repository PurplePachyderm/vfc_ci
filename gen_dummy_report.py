# Reads tests data and generates the HTML report

import numpy as np
import pandas as pd

from bokeh.plotting import figure, show
from bokeh.resources import INLINE
from bokeh.embed import components

from jinja2 import Environment, FileSystemLoader


    # Generate a random box plot
    # (copied from https://docs.bokeh.org/en/latest/docs/gallery/boxplot.html)

def genBoxPlot():
    # generate some synthetic time series for six different categories
    cats = list("abcdef")
    yy = np.random.randn(2000)
    g = np.random.choice(cats, 2000)
    for i, l in enumerate(cats):
        yy[g == l] += i // 2
    df = pd.DataFrame(dict(score=yy, group=g))

    # find the quartiles and IQR for each category
    groups = df.groupby('group')
    q1 = groups.quantile(q=0.25)
    q2 = groups.quantile(q=0.5)
    q3 = groups.quantile(q=0.75)
    iqr = q3 - q1
    upper = q3 + 1.5*iqr
    lower = q1 - 1.5*iqr

    # find the outliers for each category
    def outliers(group):
        cat = group.name
        return group[(group.score > upper.loc[cat]['score']) | (group.score < lower.loc[cat]['score'])]['score']
    out = groups.apply(outliers).dropna()

    # prepare outlier data for plotting, we need coordinates for every outlier.
    if not out.empty:
        outx = list(out.index.get_level_values(0))
        outy = list(out.values)

    p = figure(tools="", background_fill_color="#efefef", x_range=cats, toolbar_location=None)

    # if no outliers, shrink lengths of stems to be no longer than the minimums or maximums
    qmin = groups.quantile(q=0.00)
    qmax = groups.quantile(q=1.00)
    upper.score = [min([x,y]) for (x,y) in zip(list(qmax.loc[:,'score']),upper.score)]
    lower.score = [max([x,y]) for (x,y) in zip(list(qmin.loc[:,'score']),lower.score)]

    # stems
    p.segment(cats, upper.score, cats, q3.score, line_color="black")
    p.segment(cats, lower.score, cats, q1.score, line_color="black")

    # boxes
    p.vbar(cats, 0.7, q2.score, q3.score, fill_color="#E08E79", line_color="black")
    p.vbar(cats, 0.7, q1.score, q2.score, fill_color="#3B8686", line_color="black")

    # whiskers (almost-0 height rects simpler than segments)
    p.rect(cats, lower.score, 0.2, 0.01, line_color="black")
    p.rect(cats, upper.score, 0.2, 0.01, line_color="black")

    # outliers
    if not out.empty:
        p.circle(outx, outy, size=6, color="#F38630", fill_alpha=0.6)

    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = "white"
    p.grid.grid_line_width = 2
    p.xaxis.major_label_text_font_size="16px"

    return p




    # Init template loader
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('dummy_report.j2')


    # Data processing, plot generation

# Create first Bokeh plots (simple line plot)
x = [1, 2, 3, 4, 5]
y = [6, 7, 2, 4, 5]

# create a new plot with a title and axis labels
p1 = figure(title="Simple line example", x_axis_label="x", y_axis_label="y")

# add a line renderer with legend and line thickness
p1.line(x, y, legend_label="Temp.", line_width=2)

# Second plot in dedicated function (box plot)
p2 = genBoxPlot()

# Generate JS/CSS for the plots
bokeh_js = INLINE.render_js()
bokeh_css = INLINE.render_css()

plots = {
    'plot1': p1,
    'plot2': p2
}
bokeh_script, div = components(plots)


    # Render templates
render = template.render(arg='world',
                         bokeh_js=bokeh_js,
                         bokeh_css=bokeh_css,
                         bokeh_script=bokeh_script,
                         myplot=div)


    # Write template
with open("report.html", "w") as fh:
    fh.write(render)
