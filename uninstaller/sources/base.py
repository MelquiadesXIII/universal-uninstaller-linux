"""Common contract for installation sources."""

from __future__ import annotations

from typing import Protocol

from ..models import Installation, Options, Plan


class Source(Protocol):
    """Minimal source interface."""

    name: str

    def available(self) -> bool:
        """Return whether the source tools are available."""

    def detect(self, term: str) -> list[Installation]:
        """Detect installations without modifying the system."""

    def plan(self, inst: Installation, opts: Options) -> Plan:
        """Build steps without executing them."""

    def verify(self, inst: Installation) -> bool:
        """Check whether the installation is still present."""
