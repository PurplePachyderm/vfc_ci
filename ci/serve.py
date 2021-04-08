# Server for the Verificarlo CI report. This is simply a wrapper that avoids
# calling Bokeh directly.

import os

def serve(show, git_directory, git_url, port, allow_origin):

    show = "--show" if show else ""

    git = ""
    if git_directory != None:
        git = "directory %s" % git_directory
    if git_url != None:
        git = "url %s" % git_url

    dirname = os.path.dirname(__file__)
    command = "bokeh serve %s/vfc_ci_server %s --allow-websocket-origin=%s:%s --port %s --args %s" \
    % (dirname, show, allow_origin, port, port, git)

    os.system(command)
