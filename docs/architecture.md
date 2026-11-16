# Architecture

## Data flow

```text
CLI
  -> Orchestrator
     -> Source.detect()
     -> Source.plan()
     -> safety checks
     -> confirmation
     -> Executor
        -> runner / trash
```

Sources detect installations and build plans. They must not mutate the system.
`runner.py` is the only module that invokes `subprocess`; `executor.py` is the
only module allowed to perform mutations.

## Core models

- `Evidence` links an installation to observable proof.
- `Installation` describes the source, identity, scope, paths, and state.
- `Step` describes one planned operation.
- `Plan` contains steps, warnings, and an optional block reason.
- `Result` reports execution status and failed steps.
- `Options` carries CLI choices such as `purge`, `cleanup`, and `dry_run`.

## Sources

Every source follows the interface in `uninstaller/sources/base.py`:

```python
class Source(Protocol):
    name: str
    def available(self) -> bool: ...
    def detect(self, term: str) -> list[Installation]: ...
    def plan(self, inst: Installation, opts: Options) -> Plan: ...
    def verify(self, inst: Installation) -> bool: ...
```

Detection is read-only. Planning creates `Step` objects. Verification is
available to confirm that an installation remains absent, although the current
CLI does not invoke a post-execution verification pass.

## Entry points

- `python3 -m uninstaller` calls `uninstaller/__main__.py`.
- `install.sh` builds a zipapp at `~/.local/bin/uninstall`.
- `cli.py` owns argument parsing and exit-code translation.
