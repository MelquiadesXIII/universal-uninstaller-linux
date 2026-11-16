"""Orchestration of detection, selection, planning, and execution."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from . import aliases, ui
from .executor import execute
from .models import Installation, Options, Plan, Result
from .sources.apt import AptSource
from .sources.appimage import AppImageSource
from .sources.brew import BrewSource
from .sources.flatpak import FlatpakSource
from .sources.manual import ManualSource
from .sources.pipx import PipxSource
from .util import valid_term

ALWAYS_AMBIGUOUS = frozenset({"dolphin", "code"})


@dataclass(frozen=True)
class Resolution:
    """Result of the selection phase."""

    status: str
    candidates: tuple[Installation, ...] = ()
    plan: Plan | None = None


class Orchestrator:
    """Coordinate sources without letting them perform mutations."""

    def __init__(self, sources: list[object] | None = None) -> None:
        self.sources = sources or [
            AptSource(),
            FlatpakSource(),
            BrewSource(),
            PipxSource(),
            AppImageSource(),
            ManualSource(),
        ]

    def available_sources(self) -> list[object]:
        return [source for source in self.sources if source.available()]

    def detect(self, term: str, *, source_name: str | None = None) -> list[Installation]:
        candidates: list[Installation] = []
        for source in self.available_sources():
            if source_name and source.name != source_name:
                continue
            for expanded in aliases.expand(term):
                candidates.extend(source.detect(expanded))
        return _deduplicate(candidates)

    def resolve(self, term: str, *, source_name: str | None = None, tty: bool | None = None) -> Resolution:
        if not valid_term(term):
            return Resolution("usage")
        candidates = self.detect(term, source_name=source_name)
        if not candidates:
            return Resolution("not_found")
        if len(candidates) > 1 or (source_name is None and term.casefold() in ALWAYS_AMBIGUOUS):
            if tty is None:
                tty = sys.stdin.isatty()
            if not tty:
                return Resolution("ambiguous", tuple(candidates))
            return Resolution("ambiguous", tuple(candidates))
        return Resolution("ok", tuple(candidates))

    def make_plan(self, installation: Installation, options: Options) -> Plan:
        source = next(source for source in self.sources if source.name == installation.source)
        return source.plan(installation, options)

    def run(
        self,
        term: str,
        options: Options,
        *,
        source_name: str | None = None,
        tty: bool | None = None,
        home: Path | None = None,
    ) -> tuple[Resolution, Result | None]:
        resolution = self.resolve(term, source_name=source_name, tty=tty)
        if resolution.status != "ok":
            return resolution, None
        plan = self.make_plan(resolution.candidates[0], options)
        if plan.blocked_reason:
            return Resolution("blocked", resolution.candidates, plan), None
        if options.dry_run:
            return Resolution("ok", resolution.candidates, plan), None
        if not options.yes and not ui.confirm("Execute this plan?"):
            return Resolution("cancelled", resolution.candidates, plan), None
        result = execute(plan, home=home)
        return Resolution("ok", resolution.candidates, plan), result


def _deduplicate(candidates: list[Installation]) -> list[Installation]:
    seen: set[tuple[str, str]] = set()
    unique: list[Installation] = []
    for candidate in candidates:
        key = (candidate.source, candidate.ident)
        if key not in seen:
            seen.add(key)
            unique.append(candidate)
    return unique
