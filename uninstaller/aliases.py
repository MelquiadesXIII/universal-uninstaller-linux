"""Approved aliases to speed detection without replacing evidence."""

from __future__ import annotations

ALIASES = {
    "free download manager": ("freedownloadmanager",),
    "fdm": ("freedownloadmanager",),
    "dolphin-emu": ("dolphin-emu", "dolphin emulator"),
    "dolphin emulator": ("dolphin-emu", "dolphin emulator"),
    "dolphin": ("dolphin", "dolphin-emu", "dolphin emulator"),
    "vscode": ("code", "code-insiders"),
    "visual studio code": ("code", "code-insiders"),
    "brave": ("brave-browser",),
    "brave browser": ("brave-browser",),
    "docker": ("docker",),
    "postgres": ("postgresql",),
    ".net": ("dotnet",),
    "dotnet sdk": ("dotnet",),
    "r": ("r-base",),
    "appimagelauncher": ("appimagelauncher",),
    "github cli": ("gh",),
    "pipx": ("pipx",),
    "beekeeper": ("beekeeper-studio",),
    "beekeeper studio": ("beekeeper-studio",),
    "homebrew": ("brew",),
}


def expand(term: str) -> tuple[str, ...]:
    """Return the term and its aliases without duplicates."""

    values = ALIASES.get(term.casefold(), (term,))
    return tuple(dict.fromkeys(values))
