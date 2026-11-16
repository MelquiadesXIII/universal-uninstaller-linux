"""Command-line interface for the uninstaller."""

from __future__ import annotations

import argparse
import os
import sys

from .executor import execute
from .models import Options
from .orchestrator import Orchestrator
from . import ui
from .config import (
    EXIT_AMBIGUOUS,
    EXIT_BLOCKED,
    EXIT_CANCELLED,
    EXIT_FAILED,
    EXIT_NOT_FOUND,
    EXIT_OK,
    EXIT_PARTIAL,
    EXIT_USAGE,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="uninstall")
    parser.add_argument("application", nargs="?")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--sources", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--source", choices=("apt", "flatpak", "brew", "pipx", "appimage", "manual"))
    parser.add_argument("--purge", action="store_true")
    parser.add_argument("--cleanup", action="store_true")
    parser.add_argument("-y", "--yes", action="store_true")
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser


def main(argv: list[str] | None = None, *, orchestrator: Orchestrator | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.sources:
        for source in (orchestrator or Orchestrator()).sources:
            state = "available" if source.available() else "not found"
            ui.message("[INFO]", f"{source.name} {state}")
        return EXIT_OK
    if args.application is None:
        return EXIT_USAGE
    if os.geteuid() == 0:
        ui.message("[ERROR]", "Running the uninstaller as root is not allowed.", error=True)
        return EXIT_USAGE
    active = orchestrator or Orchestrator()
    options = Options(args.dry_run, args.purge, args.cleanup, args.yes, args.verbose)
    resolution = active.resolve(args.application, source_name=args.source)
    if resolution.status == "usage":
        return EXIT_USAGE
    if resolution.status == "not_found":
        ui.message("[WARN]", "Application not found.")
        return EXIT_NOT_FOUND
    if resolution.status == "ambiguous":
        for candidate in resolution.candidates:
            ui.message("[FOUND]", f"{candidate.source}\t{candidate.display_name}\t{candidate.ident}")
        return EXIT_AMBIGUOUS
    installation = resolution.candidates[0]
    plan = active.make_plan(installation, options)
    ui.message("[FOUND]", f"{installation.source}\t{installation.display_name}")
    if args.list:
        return EXIT_OK
    if plan.blocked_reason:
        ui.message("[BLOCK]", plan.blocked_reason, error=True)
        return EXIT_BLOCKED
    _print_plan(plan)
    if args.dry_run:
        ui.message("[INFO]", "Dry-run: nothing was changed.")
        return EXIT_OK
    if not args.yes and not ui.confirm("Execute this plan?"):
        return EXIT_CANCELLED
    result = execute(plan)
    if result.status == "ok":
        return EXIT_OK
    if result.status == "partial":
        return EXIT_PARTIAL
    return EXIT_FAILED


def _print_plan(plan) -> None:
    for index, step in enumerate(plan.steps, 1):
        ui.message("[PLAN]", f"{index}. {step.description}")
    for warning in plan.warnings:
        ui.message("[WARN]", warning)


if __name__ == "__main__":
    sys.exit(main())
