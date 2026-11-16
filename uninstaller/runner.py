"""Only module authorized to invoke external processes."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from collections.abc import Mapping, Sequence


@dataclass(frozen=True)
class CommandResult:
    """Normalized result of a read-only command."""

    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


def run_read(argv: Sequence[str], *, env: Mapping[str, str] | None = None) -> CommandResult:
    """Run a query without depending on the system language."""

    command = tuple(str(item) for item in argv)
    read_env = os.environ.copy()
    read_env["LC_ALL"] = "C"
    if env is not None:
        read_env.update(env)
    completed = subprocess.run(
        list(command),
        check=False,
        capture_output=True,
        text=True,
        env=read_env,
    )
    return CommandResult(command, completed.returncode, completed.stdout, completed.stderr)


def run_mutating(argv: Sequence[str]) -> int:
    """Run a mutating command inheriting the terminal and return its code."""

    command = [str(item) for item in argv]
    return subprocess.run(command, check=False).returncode


def validate_sudo() -> int:
    """Validate credentials once without depending on sudo output text."""

    return run_mutating(["sudo", "-v"])
