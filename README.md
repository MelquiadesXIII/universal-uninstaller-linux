# Universal Uninstaller

Evidence-based application uninstaller for Linux. It detects APT/.deb, Flatpak, Homebrew, pipx, AppImage, and manual installations, shows a plan before changes, protects critical packages, and sends user files to the desktop trash instead of permanently deleting them.

> **Development status:** early release. Review the current limitations before using it on a production system.

## What it supports

| Source | Current behavior |
|---|---|
| APT/dpkg | Package detection, suite grouping, removal simulation, removal, and optional purge |
| Flatpak | User/system application detection and uninstall planning |
| Homebrew | Formula/cask detection; Homebrew itself is protected |
| pipx | Package and exposed-app detection |
| AppImage | Magic-byte detection and verified-file trash plans |
| Manual | Evidence-based executable and desktop-entry detection |

## Quick start

From a checkout:

```bash
python3 -m uninstaller --sources
python3 -m uninstaller --dry-run <application>
python3 -m uninstaller <application>
```

Install the zipapp locally:

```bash
sh install.sh
~/.local/bin/uninstall --sources
```

The installer does not edit shell startup files. If necessary, add `~/.local/bin` to `PATH` manually.

## Documentation

- [Usage guide](docs/usage.md)
- [Safety model](docs/safety.md)
- [Architecture](docs/architecture.md)
- [Development guide](docs/development.md)

## Contributing

```bash
python3 -m unittest discover -v
```

Please keep changes focused, add mocked tests for new behavior, and never run destructive commands during development.

## License

This project is released under the [MIT License](LICENSE).
