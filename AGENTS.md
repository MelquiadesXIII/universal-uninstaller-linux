# Universal Uninstaller — Agent Guide

You are the agent implementing the `uninstall` command. Keep the implementation, comments, user-facing messages, and documentation in English.

## Reference documents

Read these documents completely before making implementation decisions:

1. `README.md` — project scope and user-facing behavior.
2. `docs/architecture.md` — architecture and source responsibilities.
3. `docs/safety.md` — safety rules and protected data.
4. `docs/development.md` — testing and contribution workflow.

If the plan conflicts with your judgment, do not improvise. Stop and ask for clarification.

## Required workflow

1. Work on one milestone at a time (H1 through H10). At the end of each milestone, stop, summarize the changes, report the tests, and wait for approval before continuing.
2. During development, do not modify the host system. Never run real uninstall commands, `sudo`, package removals, or permanent deletion. Read-only commands, `--dry-run`, `--list`, and mock-based tests are allowed.
3. Tests must never use the real system. Replace `runner` with a test double, use `tempfile` with a simulated `$HOME`, and never invoke real `subprocess` calls from tests.
4. Use only the Python standard library. Do not install packages with pip or a system package manager.
5. `subprocess` may be used only in `runner.py`; only `executor.py` may perform system mutations.
6. Never permanently delete user files. Move them to the trash; if trash handling fails, fail the step without falling back to `rm`.
7. Never use `rm -f`, `--force`, `--ignore-dependencies`, `shopt`, `eval`, or `shell=True`. Use argument lists and `--` before user-controlled names.
8. Never execute an AppImage, including with `--appimage-version`. Inspect magic bytes only.
9. Never edit shell configuration files such as `.bashrc` or `.profile`; report required changes instead.
10. Homebrew itself is `NEVER_AUTO`: provide warnings and official instructions only, with no executable removal steps.
11. If evidence is insufficient, stop and explain what is missing. Do not fill gaps with assumptions.

## Initial system reconnaissance

Before writing code, run and report these read-only checks:

```text
python3 --version
sudo --version | head -n 2
command -v gio flatpak brew pipx dpkg-query apt-get apt-cache systemctl getent
flatpak --version; pipx --version; brew --version
cat /etc/os-release | head -n 4
ls ~/.local/bin ~/Applications /opt 2>/dev/null
```

Adjust the plan if the environment differs from the assumptions, and ask before continuing when the difference affects behavior or safety.

## Fixture capture

With the user's permission, capture read-only command output under `tests/fixtures/` using `LC_ALL=C`:

- `dpkg-query -W -f='${binary:Package}\t${Version}\t${db:Status-Abbrev}\t${Essential}\t${Protected}\n'`
- `apt-mark showmanual`
- `flatpak list --app --columns=application,name,installation,origin`
- `pipx list --json`
- `brew list --formula` and `brew list --cask`, when available
- One representative `.desktop` file for each supported installation type

Warn the user that fixtures may contain installed application names. Do not upload or share them outside the local machine.

## Milestone handoff format

At the end of every milestone, report:

1. Files created or modified.
2. Output from `python3 -m unittest discover -v`.
3. Decisions made outside the plan.
4. Open questions or risks.
5. What the next milestone will address.

## Code conventions

- Support Python 3.10 or newer; confirm the actual version during reconnaissance.
- Use type annotations and `from __future__ import annotations`.
- Keep one responsibility per module and prefer small, clearly named functions.
- Keep user-facing messages in English with `[INFO]`, `[FOUND]`, `[PLAN]`, `[WARN]`, `[BLOCK]`, `[ERROR]`, and `[OK]` prefixes.
- Write the complete log to `~/.local/state/uninstall/uninstall.log`, including the command, return code, and timestamp.
- Do not depend on `sudo` error text; use return codes only.
- Capture read-only command output with `LC_ALL=C`; mutating commands inherit the terminal.

## Stop and ask when

- Actual command output does not match a fixture or the expected format.
- A safety decision is not covered by the plan, such as a safe path or critical package classification.
- A system-mutating command would be required.
- A new alias, suite, or critical pattern is needed but is not documented and approved.
