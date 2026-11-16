"""Persistent command and result logging."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from collections.abc import Sequence

from .config import log_path


def write_event(
    argv: Sequence[str],
    returncode: int,
    *,
    home: Path | None = None,
    timestamp: datetime | None = None,
) -> None:
    """Append an event to the log, creating its directory when needed."""

    destination = log_path(home)
    destination.parent.mkdir(parents=True, exist_ok=True)
    moment = timestamp or datetime.now(timezone.utc)
    command = " ".join(str(part) for part in argv)
    with destination.open("a", encoding="utf-8") as stream:
        stream.write(f"{moment.isoformat()}\t{returncode}\t{command}\n")
