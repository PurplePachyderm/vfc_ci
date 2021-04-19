# Server for the Verificarlo CI report. This is simply a wrapper that avoids
# calling Bokeh directly.

import os

def serve(show, git_directory, git_url, port, allow_origin, logo_url):

    show = "--show" if show else ""

    git = ""
    if git_directory != None:
        git = "git directory %s" % git_directory
    if git_url != None:
        git = "git url %s" % git_url

    logo = ""
    if logo_url != None:
        logo = "logo %s" % logo_url


    dirname = os.path.dirname(__file__)
    command = "bokeh serve %s/vfc_ci_server %s --allow-websocket-origin=%s:%s --port %s --args %s %s" \
    % (dirname, show, allow_origin, port, port, git, logo)

    os.system(command)
