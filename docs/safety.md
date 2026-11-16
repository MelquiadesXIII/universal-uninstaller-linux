# Safety model

## Before execution

The orchestrator validates the application term, expands aliases, detects
installations, resolves ambiguity, creates a plan, and checks safety before
execution. Use `--dry-run` to inspect the plan without mutation.

The program refuses to run as root. Do not prefix it with `sudo`.

## APT protection

APT plans run:

```text
apt-get -s remove -- <packages>
```

If the simulation includes configured critical packages, the plan is blocked.
Critical patterns include package-management tools, `libc6`, `systemd`, `sudo`,
desktop metapackages, Plasma, `dolphin`, kernel packages, and graphics stacks.

APT packages in `rc` state are reported as already uninstalled. They are only
purged when `--purge` is explicitly supplied.

## Files and trash

User files are sent through `gio trash -- <path>` when `gio` is available.
Otherwise the built-in XDG Trash implementation uses:

```text
~/.local/share/Trash/files/
~/.local/share/Trash/info/
```

Trash failure does not fall back to permanent deletion. Root paths are limited
to verified locations and use `sudo rm -r --one-file-system -- <path>`.

## Never executed or removed automatically

- AppImages are never executed; only magic bytes are inspected.
- Shell startup files are never edited.
- Homebrew itself produces no executable removal step.
- Application data, Docker data, PostgreSQL clusters, Ollama models, and
  system users are preserved or reported.
- APT repositories and keys are not removed.

## Confirmation

Normal execution asks one CLI confirmation. The current implementation's
`--yes` flag skips that confirmation even when a plan is marked with extra
confirmation risk. Package managers may still ask their own prompts.

## Development rule

Tests must use mocks and temporary directories. Do not run real uninstall
commands, `sudo`, package removal, or permanent deletion while developing.
