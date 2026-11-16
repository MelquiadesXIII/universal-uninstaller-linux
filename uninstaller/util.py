"""Small parsing and validation helpers shared by sources."""

from __future__ import annotations

import re
import shlex
from dataclasses import dataclass
from pathlib import Path


TERM_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+:@-]*$")
_FIELD_CODES = re.compile(r"%[fFuUdDnNickvm]")
_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=.*$")


@dataclass(frozen=True)
class DesktopEntry:
    """Relevant fields from a .desktop file."""

    name: str | None
    exec_argv: tuple[str, ...]
    icon: str | None
    path: Path | None = None


def parse_desktop(text: str, *, path: Path | None = None) -> DesktopEntry:
    """Extract Name, Icon, and Exec without executing their contents."""

    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key in {"Name", "Exec", "Icon"} and key not in values:
            values[key] = value.strip()
    return DesktopEntry(
        name=values.get("Name"),
        exec_argv=parse_exec(values.get("Exec", "")),
        icon=values.get("Icon"),
        path=path,
    )


def parse_exec(value: str) -> tuple[str, ...]:
    """Convert Exec into arguments, removing `env`, assignments, and field codes."""

    if not value:
        return ()
    try:
        tokens = shlex.split(value, comments=False, posix=True)
    except ValueError:
        return ()
    while tokens and (tokens[0] == "env" or _ASSIGNMENT.fullmatch(tokens[0])):
        tokens.pop(0)
    cleaned = (_FIELD_CODES.sub("", token) for token in tokens if token)
    return tuple(token for token in cleaned if token)


def valid_term(term: str) -> bool:
    """Validate a term before turning it into a command argument."""

    return bool(TERM_RE.fullmatch(term))


def has_parent_component(path: Path) -> bool:
    """Return whether the written path contains a `..` component."""

    return ".." in path.parts
