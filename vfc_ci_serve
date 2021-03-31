#!/usr/bin/env bash

# Simple wrapper to avoid calling Bokeh directly and pass our own arguments

# Parse arguments

SHOW=""
LINK_REPOSITORY=""
ALLOW_ORIGIN=""
PORT=8080

for (( i=1; i<=$#; i++)); do
    j=$((i+1))

    case ${!i} in
        -s|--show)
        SHOW="--show"
        ;;
        -gd|--git-directory)
        LINK_REPOSITORY="directory ${!j}"
        ;;
        -gr|--git-remote)
        LINK_REPOSITORY="remote ${!j}"
        ;;
        -a|--allow-origin)
        ALLOW_ORIGIN="--allow-websocket-origin=${!j}"
        ;;
        -p|--port)
        PORT=${!j}
        ;;
    esac

done


# Launch the Bokeh server
bokeh serve vfc_ci_server $SHOW $CUSTOM_PORT $ALLOW_ORIGIN --port $PORT --args $LINK_REPOSITORY
