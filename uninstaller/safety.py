"""Safety checks before any destructive step."""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path

from .config import CRITICAL_PATTERNS, EXTRA_CONFIRM_PATTERNS


def critical_level(
    name: str,
    *,
    essential: bool = False,
    protected: bool = False,
) -> str:
    """Classify a package as normal, extra-confirmation, or blocked."""

    if essential or protected or any(fnmatch.fnmatch(name, pattern) for pattern in CRITICAL_PATTERNS):
        return "blocked"
    if any(fnmatch.fnmatch(name, pattern) for pattern in EXTRA_CONFIRM_PATTERNS):
        return "extra_confirm"
    return "normal"


def simulation_criticals(lines: str) -> list[str]:
    """Extract critical package names from APT `Remv` lines."""

    found: list[str] = []
    for line in lines.splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[0] == "Remv":
            name = fields[1]
            if critical_level(name) == "blocked":
                found.append(name)
    return found


def validate_path(
    path: Path,
    *,
    home: Path | None = None,
    roots: tuple[Path, ...] = (),
) -> tuple[bool, str]:
    """Check that an existing path is below an allowed root."""

    if not path.is_absolute():
        return False, "path is not absolute"
    if ".." in path.parts:
        return False, "path contains '..'"
    resolved = Path(os.path.realpath(path))
    home_path = (home or Path.home()).resolve()
    forbidden = {Path("/"), Path("/home"), home_path, Path("/usr"), Path("/etc"), Path("/var")}
    if resolved in forbidden or resolved == Path("/"):
        return False, "path is a protected root"
    if not path.exists() and not path.is_symlink():
        return False, "path no longer exists"
    for root in roots:
        root_resolved = Path(os.path.realpath(root))
        if resolved != root_resolved and root_resolved in resolved.parents:
            return True, ""
    return False, "path is outside the allowed roots"
