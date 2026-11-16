# Development

## Layout

```text
uninstaller/
├── __main__.py
├── aliases.py
├── cli.py
├── config.py
├── executor.py
├── log.py
├── models.py
├── orchestrator.py
├── runner.py
├── safety.py
├── trash.py
├── ui.py
├── util.py
└── sources/
    ├── appimage.py
    ├── apt.py
    ├── base.py
    ├── brew.py
    ├── flatpak.py
    ├── manual.py
    └── pipx.py
tests/
```

## Test command

```bash
python3 -m unittest discover -v
```

Tests replace command execution with mocks and use temporary directories.
Never use the host package database or real subprocess calls in tests.

## Adding a source

1. Implement `available`, `detect`, `plan`, and `verify` in a new
   `uninstaller/sources/<name>.py`.
2. Register the source in `Orchestrator.__init__`.
3. Add the source to the CLI `--source` choices.
4. Add focused tests for unavailable tools, detection, planning, and safety.

`detect` must be read-only and return `Installation` objects with evidence.
`plan` must not execute commands.

## Adding aliases

Add approved aliases to `uninstaller/aliases.py`. Aliases may expand searches,
but source evidence must still identify the real installation.

## Adding safety patterns

Add critical package patterns to `uninstaller/config.py` only when approved.
Add tests that prove the intended blocked or extra-confirmation behavior.

## Validation checklist

- `python3 -m unittest discover -v`
- `python3 -m uninstaller --sources`
- `python3 -m uninstaller --list <known-application>`
- `python3 -m uninstaller --dry-run <known-application>`
- No real uninstall, `sudo`, package removal, AppImage execution, or permanent
  deletion during development.

## Known gaps

- The log writer exists but is not connected to normal CLI execution.
- The CLI does not print a final execution summary.
- Post-execution source verification is not currently wired into the orchestrator.
- `--verbose` and color control are accepted but not implemented.
- Fuzzy “did you mean?” suggestions are not implemented.
