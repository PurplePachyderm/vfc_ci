# Server for the Verificarlo CI report. This is simply a wrapper to avoid
# calling Bokeh directly.

import os
import calendar
import time
import json

# Magic numbers
default_timeframe_width = 90 * 86400  # 90 days


def run(directory, show, port, allow_origin, logo_url, max_files):
    '''Entry point of vfc_ci serve'''

    # Prepare arguments
    directory = "directory %s" % directory

    show = "--show" if show else ""

    logo = "logo %s" % logo_url if logo_url else ""

    max_files = "max_files %s" % max_files if max_files else ""

    dirname = os.path.dirname(__file__)

    # Call the "bokeh serve" command on the system
    command = "bokeh serve %s/vfc_ci_report %s --allow-websocket-origin=%s:%s --port %s --args %s %s %s" \
        % (dirname, show, allow_origin, port, port, directory, logo, max_files)
    command = os.path.normpath(command)

    os.system(command)
