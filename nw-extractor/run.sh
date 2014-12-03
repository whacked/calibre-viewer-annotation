#!/bin/bash

if [[ `uname` == "Darwin" ]]; then
    /Applications/node-webkit.app/Contents/MacOS/node-webkit . "$@"
else
    MYAPP_WRAPPER="`readlink -f "$0"`"
    HERE="`dirname "$MYAPP_WRAPPER"`"
    # Always use our versions of ffmpeg libs.
    # This also makes RPMs find our library symlinks.
    export LD_LIBRARY_PATH=$([ -n "$LD_LIBRARY_PATH" ] && echo "$HERE:$HERE/lib:$LD_LIBRARY_PATH" || echo "$HERE:$HERE/lib")
    echo $LD_LIBRARY_PATH

    exec -a "$0" "/opt/node-webkit-v0.11.1-linux-x64/nw" . "$@"
fi
