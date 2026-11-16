#!/bin/sh
set -eu

destination="${HOME}/.local/bin/uninstall"
mkdir -p "${HOME}/.local/bin"
python3 -m zipapp uninstaller -o "${destination}" -p '/usr/bin/env python3'
chmod +x "${destination}"
"${destination}" --sources
