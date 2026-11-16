"""User output and confirmations."""

from __future__ import annotations

import os
import sys


def message(prefix: str, text: str, *, error: bool = False) -> None:
    """Write a message with the agreed prefix."""

    stream = sys.stderr if error else sys.stdout
    print(f"{prefix} {text}", file=stream)


def color_enabled(no_color: bool = False) -> bool:
    """Return whether ANSI output can be used."""

    return not no_color and "NO_COLOR" not in os.environ and sys.stdout.isatty()


def confirm(prompt: str, *, default: bool = False) -> bool:
    """Request a simple confirmation without assuming an affirmative answer."""

    suffix = "[Y/n]" if default else "[y/N]"
    try:
        answer = input(f"{prompt} {suffix} ").strip().lower()
    except EOFError:
        return False
    if not answer:
        return default
    return answer in {"y", "yes"}
