#!/bin/bash

set -xeo pipefail

DEST_DIR=$1
WHEEL=$2
DELOCATE_ARCHS=$3
if [[ "$RUNNER_OS" == "Linux" ]]; then
    auditwheel repair -w $DEST_DIR $WHEEL
elif [[ "$RUNNER_OS" == "macOS" ]]; then
    delocate-wheel --require-archs $DELOCATE_ARCHS -w $DEST_DIR -v $WHEEL
fi

if [[ "$(python -c 'import platform; print(platform.python_implementation())')" == "CPython" ]]; then
    pipx run abi3audit --strict --report $WHEEL
fi
