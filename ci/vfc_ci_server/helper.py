# General helper functions for both compare_runs and compare_variables

import calendar;
import time;

################################################################################


# From a timestamp, return the associated metadata as a Pandas serie
def get_metadata(metadata, timestamp):
    return metadata.loc[timestamp]


# Returns the string for a tick of the runs' x-axis (a string that indicates the
# elapsed time since the run)
def runs_tick_string(timestamp, hash):

    gmt = time.gmtime()
    now = calendar.timegm(gmt)
    diff = now - timestamp


    # Special case : < 1 minute (return string directly)
    if diff < 60:
        str = "Less than a minute ago"
        if hash != "":
            str = str + " (%s)" % hash
        return str

    # < 1 hour
    if diff < 3600:
        n = int(diff / 60)
        str = "%s minute%s ago"
    # < 1 day
    elif diff < 86400:
        n = int(diff / 3600)
        str = "%s hour%s ago"
    # < 1 week
    elif diff < 604800:
        n = int(diff / 86400)
        str = "%s day%s ago"
    # < 1 month
    elif diff < 2592000:
        n = int(diff / 604800)
        str = "%s week%s ago"
    # > 1 month
    else:
        n = diff / 2592000
        str = "%s month%s ago"

    plural = ""
    if n != 1:
        plural = "s"

    str = str % (n, plural)


    # We might want to add the git hash
    if hash != "":
        str = str + " (%s)" % hash

    return str
