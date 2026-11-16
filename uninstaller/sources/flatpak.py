"""Flatpak source for user and system applications."""

from __future__ import annotations

import shutil

from .. import runner
from ..models import Evidence, Installation, Options, Plan, Risk, Step


class FlatpakSource:
    """Detect Flatpak applications without touching their user data."""

    name = "flatpak"

    def available(self) -> bool:
        return shutil.which("flatpak") is not None

    def detect(self, term: str) -> list[Installation]:
        if not self.available():
            return []
        result = runner.run_read(
            ["flatpak", "list", "--app", "--columns=application,name,installation,origin"]
        )
        if result.returncode != 0:
            return []
        matches: list[Installation] = []
        for line in result.stdout.splitlines():
            fields = line.split("\t")
            if len(fields) < 3:
                continue
            app_id, name, installation = fields[:3]
            origin = fields[3] if len(fields) > 3 else ""
            if term.casefold() not in {app_id.casefold(), name.casefold()}:
                continue
            scope = "user" if installation == "user" else "system"
            matches.append(
                Installation(
                    self.name,
                    app_id,
                    name,
                    None,
                    scope,
                    evidence=[Evidence("flatpak", f"{app_id} ({origin})", 3)],
                    extras={"origin": origin},
                )
            )
        return matches

    def plan(self, inst: Installation, opts: Options) -> Plan:
        scope = "--user" if inst.scope == "user" else "--system"
        steps = [
            Step(
                "run",
                f"Uninstall Flatpak {inst.ident} ({inst.scope})",
                argv=["flatpak", "uninstall", scope, inst.ident],
                risk=Risk.NORMAL,
            )
        ]
        if opts.cleanup:
            steps.append(
                Step(
                    "run",
                    "Review unused Flatpak runtimes",
                    argv=["flatpak", "uninstall", "--unused"],
                    risk=Risk.EXTRA_CONFIRM,
                )
            )
        warnings = [f"Preserving ~/.var/app/{inst.ident} (user data)."]
        return Plan(inst, steps=steps, warnings=warnings)

    def verify(self, inst: Installation) -> bool:
        return bool(self.detect(inst.ident))
