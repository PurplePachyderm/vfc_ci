# Server for the Verificarlo CI report. This is simply a wrapper to avoid
# calling Bokeh directly.

import os
import calendar
import time
import json

# Magic numbers
default_timeframe_width = 90 * 86400  # 90 days


def run(directory, show, port, allow_origin, logo_url, timeframe):
    '''Entry point of vfc_ci serve'''

    # Prepare arguments
    directory = "directory %s" % directory

    show = "--show" if show else ""

    logo = "logo %s" % logo_url if logo_url else ""

    # If only until is specified
    if timeframe["from"] is None and timeframe["until"] is not None:
        timeframe["from"] = 0

    # If only from is specified
    if timeframe["until"] is None and timeframe["from"] is not None:
        timeframe["until"] = calendar.timegm(time.gmtime())

    # If nothing is specified (default behaviour)
    if timeframe["from"] is None and timeframe["until"] is None:
        timeframe["until"] = calendar.timegm(time.gmtime())
        timeframe["from"] = timeframe["until"] - default_timeframe_width

    timeframe = "timeframe " + \
        str(timeframe["from"]) + " " + str(timeframe["until"])

    dirname = os.path.dirname(__file__)

    # Call the "bokeh serve" command on the system
    command = "bokeh serve %s/vfc_ci_report %s --allow-websocket-origin=%s:%s --port %s --args %s %s %s" \
        % (dirname, show, allow_origin, port, port, directory, logo, timeframe)
    command = os.path.normpath(command)

    os.system(command)
