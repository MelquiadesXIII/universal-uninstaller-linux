"""Safe AppImage detection using magic bytes and desktop entries."""

from __future__ import annotations

import os
from pathlib import Path

from ..models import Evidence, Installation, Options, Plan, Risk, Step
from ..util import parse_desktop


class AppImageSource:
    """Never execute an AppImage; only inspect files and desktop entries."""

    name = "appimage"

    def __init__(self, home: Path | None = None) -> None:
        self.home = (home or Path.home()).expanduser()

    def available(self) -> bool:
        return True

    def detect(self, term: str) -> list[Installation]:
        candidates: dict[Path, tuple[str, list[Path]]] = {}
        for directory in self._directories():
            if not directory.is_dir():
                continue
            for path in directory.iterdir():
                if path.is_file() and self._is_appimage(path):
                    candidates.setdefault(path, (path.stem, []))
        for desktop in self._desktop_files():
            try:
                entry = parse_desktop(desktop.read_text(encoding="utf-8", errors="replace"), path=desktop)
            except OSError:
                continue
            if not entry.exec_argv:
                continue
            target = Path(entry.exec_argv[0]).expanduser()
            if target.is_file() and self._is_appimage(target):
                name, desktops = candidates.setdefault(target, (entry.name or target.stem, []))
                candidates[target] = (name, [*desktops, desktop])
        matches: list[Installation] = []
        for path, (name, desktops) in candidates.items():
            if term.casefold() not in {name.casefold(), path.stem.casefold()}:
                continue
            paths = [path, *desktops]
            matches.append(
                Installation(
                    self.name,
                    str(path),
                    name,
                    None,
                    "user" if path.is_relative_to(self.home) else "system",
                    paths=paths,
                    evidence=[Evidence("magic-bytes", str(path), 3)],
                    extras={"desktop_files": desktops},
                )
            )
        return matches

    def plan(self, inst: Installation, opts: Options) -> Plan:
        return Plan(
            inst,
            steps=[
                Step(
                    "trash" if path.is_relative_to(self.home) else "root_rm",
                    f"Move to trash {path}",
                    path=path,
                    needs_root=not path.is_relative_to(self.home),
                    risk=Risk.NORMAL,
                )
                for path in inst.paths
            ],
            warnings=["Application configuration and data are preserved."],
        )

    def verify(self, inst: Installation) -> bool:
        return any(path.exists() for path in inst.paths)

    def _directories(self) -> tuple[Path, ...]:
        return (
            self.home / "Applications",
            self.home / "Downloads",
            self.home / "Descargas",
            self.home / ".local/bin",
            Path("/opt"),
        )

    def _desktop_files(self) -> list[Path]:
        directories = (self.home / ".local/share/applications", Path("/usr/share/applications"))
        return [path for directory in directories if directory.is_dir() for path in directory.glob("*.desktop")]

    @staticmethod
    def _is_appimage(path: Path) -> bool:
        try:
            with path.open("rb") as stream:
                stream.seek(8)
                return stream.read(3) == b"AI\x02"
        except OSError:
            return False
