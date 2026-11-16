"""Punto de entrada para `python -m uninstaller`."""

from __future__ import annotations

import sys

if __package__ in {None, ""}:
    import types
    from pathlib import Path

    package = types.ModuleType("uninstaller")
    package.__path__ = [str(Path(__file__).parent)]
    sys.modules["uninstaller"] = package

from uninstaller.cli import main

sys.exit(main())
