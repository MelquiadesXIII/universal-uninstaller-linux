"""Shared uninstaller models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class Evidence:
    """Evidence relating an application to an installation."""

    kind: str
    detail: str
    strength: int


@dataclass
class Installation:
    """Installation detected by a source."""

    source: str
    ident: str
    display_name: str
    version: str | None
    scope: str
    packages: list[str] = field(default_factory=list)
    paths: list[Path] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    state: str = "installed"
    extras: dict[str, object] = field(default_factory=dict)


class Risk(Enum):
    """Risk level of a step."""

    NORMAL = "normal"
    EXTRA_CONFIRM = "extra_confirm"
    BLOCKED = "blocked"
    NEVER_AUTO = "never_auto"


@dataclass
class Step:
    """Operation that the executor can present or perform."""

    kind: str
    description: str
    argv: list[str] | None = None
    path: Path | None = None
    needs_root: bool = False
    risk: Risk = Risk.NORMAL
    verify: Callable[[], bool] | None = None


@dataclass
class Plan:
    """Plan explained before running an uninstall."""

    installation: Installation
    steps: list[Step] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    blocked_reason: str | None = None


@dataclass
class Result:
    """Aggregated execution result."""

    status: str
    done: list[Step] = field(default_factory=list)
    failed: list[Step] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Options:
    """Common options consumed by sources."""

    dry_run: bool = False
    purge: bool = False
    cleanup: bool = False
    yes: bool = False
    verbose: bool = False
