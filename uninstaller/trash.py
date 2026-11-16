"""Safe movement of user files to the XDG trash."""

from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from . import runner


def move_to_trash(path: Path, *, home: Path | None = None) -> bool:
    """Use gio or a custom XDG trash; never delete permanently."""

    gio = shutil.which("gio")
    if gio:
        return runner.run_mutating([gio, "trash", "--", str(path)]) == 0
    return _move_to_xdg_trash(path, home=home or Path.home())


def _move_to_xdg_trash(path: Path, *, home: Path) -> bool:
    trash = home / ".local" / "share" / "Trash"
    files = trash / "files"
    info = trash / "info"
    files.mkdir(parents=True, exist_ok=True)
    info.mkdir(parents=True, exist_ok=True)
    name = _unique_name(path.name, files)
    destination = files / name
    info_file = info / f"{name}.trashinfo"
    original = quote(str(path), safe="/")
    stamp = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S")
    info_file.write_text(
        f"[Trash Info]\nPath={original}\nDeletionDate={stamp}\n",
        encoding="utf-8",
    )
    try:
        try:
            os.rename(path, destination)
        except OSError as error:
            if error.errno != 18:  # EXDEV: distintos sistemas de archivos.
                raise
            shutil.move(str(path), str(destination))
    except OSError:
        info_file.unlink(missing_ok=True)
        return False
    return True


def _unique_name(name: str, directory: Path) -> str:
    candidate = name
    index = 1
    while (directory / candidate).exists():
        candidate = f"{name}.{index}"
        index += 1
    return candidate
