#!/bin/sh
set -eu

# These queries do not uninstall anything.
python3 -m uninstaller --sources

if [ "$#" -ne 1 ]; then
    printf 'Usage: %s <application>\n' "$0" >&2
    exit 2
fi

python3 -m uninstaller --list "$1"
python3 -m uninstaller --dry-run "$1"
