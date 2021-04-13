# General helper functions for both compare_runs and compare_variables

import calendar;
import time;

################################################################################


# From a timestamp, return the associated metadata as a Pandas serie
def get_metadata(metadata, timestamp):
    return metadata.loc[timestamp]


# Return a string that indicates the elapsed time since the run, used as the
# x-axis tick in "Compare runs" or when selecting run in "Inspect run"
def get_run_name(timestamp, hash):

    gmt = time.gmtime()
    now = calendar.timegm(gmt)
    diff = now - timestamp


    # Special case : < 1 minute (return string directly)
    if diff < 60:
        str = "Less than a minute ago"

        if hash != "":
            str = str + " (%s)" % hash

        if str == get_run_name.previous:
            get_run_name.counter = get_run_name.counter + 1
            str = "%s (%s)" % (str, get_run_name.counter)
        else:
            get_run_name.counter = 0
            get_run_name.previous = str

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


    # Finally, check for duplicate with previously generated string
    if str == get_run_name.previous:
        # Increment the duplicate counter and add it to str
        get_run_name.counter = get_run_name.counter + 1
        str = "%s (%s)" % (str, get_run_name.counter)

    else:
        # No duplicate, reset both previously generated str and duplicate counter
        get_run_name.counter = 0
        get_run_name.previous = str

    return str

# This will help us store data about last generated string to avoid duplicates
get_run_name.counter = 0
get_run_name.previous = ""


def reset_tick_strings():
    get_run_name.counter = 0
    get_run_name.previous = ""
