# Usage

## Run from the repository

From the repository root:

```bash
python3 -m uninstaller --help
python3 -m uninstaller --sources
python3 -m uninstaller --list wine
python3 -m uninstaller --dry-run wine
```

Use `--dry-run` before every real uninstall. Select a source when a name is ambiguous:

```bash
python3 -m uninstaller --source apt --dry-run wine
python3 -m uninstaller --source flatpak --dry-run <app-id>
python3 -m uninstaller --source brew --dry-run <formula>
python3 -m uninstaller --source pipx --dry-run <package>
```

To execute a plan:

```bash
python3 -m uninstaller <application>
```

APT configuration can be purged explicitly:

```bash
python3 -m uninstaller --source apt --purge <package>
```

## Install the zipapp

From the repository root:

```bash
sh install.sh
```

The script creates `~/.local/bin/uninstall`, makes it executable, and runs
`uninstall --sources`. It does not edit `.bashrc`, `.profile`, or other shell
startup files.

If the command is not in `PATH`:

```bash
~/.local/bin/uninstall --sources
export PATH="$HOME/.local/bin:$PATH"
```

## Options

| Option | Description |
|---|---|
| `--list` | Detect and display the selected installation without executing it |
| `--sources` | Show available sources |
| `--dry-run` | Display the plan without changing the system |
| `--source SOURCE` | Restrict detection to `apt`, `flatpak`, `brew`, `pipx`, `appimage`, or `manual` |
| `--purge` | Add an APT purge step or purge residual APT configuration |
| `--cleanup` | Add supported orphan-cleanup review steps |
| `-y`, `--yes` | Skip the CLI confirmation |
| `--no-color` | Accepted by the CLI; output is currently plain text |
| `-v`, `--verbose` | Accepted by the CLI; verbose output is currently not implemented |

## Important names

Aliases include `fdm` → `freedownloadmanager`, `postgres` → `postgresql`,
`vscode` → `code`, and `homebrew` → `brew`. Aliases only expand detection;
they never prove identity.

`dolphin` is always treated as ambiguous. Use `dolphin-emu` for the emulator
or select `--source apt` for the KDE package.

## Exit codes

| Code | Meaning |
|---:|---|
| `0` | Success, query success, or dry-run success |
| `1` | Execution failure |
| `2` | Invalid usage or root execution |
| `3` | Application not found |
| `4` | Ambiguous match |
| `5` | User cancelled |
| `6` | Partial completion |
| `7` | Blocked by safety policy |

## Self-removal

The tool refuses to uninstall itself when managed by pipx. The zipapp installed
by `install.sh` must be removed manually:

```bash
rm ~/.local/bin/uninstall
```

## Current implementation notes

The current CLI does not print a final execution summary, does not emit log
events through the available log writer, and does not provide fuzzy “did you
mean?” suggestions. See the [development guide](development.md) for known
limitations.
