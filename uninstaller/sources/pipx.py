"""pipx source based exclusively on `pipx list --json`."""

from __future__ import annotations

import json
import shutil
from collections.abc import Iterator

from .. import runner
from ..models import Evidence, Installation, Options, Plan, Risk, Step


class PipxSource:
    """Detect pipx packages and their exposed applications."""

    name = "pipx"

    def available(self) -> bool:
        return shutil.which("pipx") is not None

    def detect(self, term: str) -> list[Installation]:
        if not self.available():
            return []
        result = runner.run_read(["pipx", "list", "--json"])
        if result.returncode != 0:
            return []
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            return []
        matches: list[Installation] = []
        for package, version, apps in _packages(data):
            if term.casefold() not in {package.casefold(), *(app.casefold() for app in apps)}:
                continue
            matches.append(
                Installation(
                    self.name,
                    package,
                    package,
                    version,
                    "user",
                    evidence=[Evidence("pipx", f"{package}; apps: {', '.join(apps)}", 3)],
                    extras={"apps": apps},
                )
            )
        return matches

    def plan(self, inst: Installation, opts: Options) -> Plan:
        if inst.ident == "uninstall":
            return Plan(
                inst,
                warnings=["The uninstaller itself is protected."],
                blocked_reason="The program is not allowed to uninstall itself.",
            )
        return Plan(
            inst,
            steps=[
                Step(
                    "run",
                    f"Uninstall pipx package {inst.ident}",
                    argv=["pipx", "uninstall", inst.ident],
                    risk=Risk.NORMAL,
                )
            ],
        )

    def verify(self, inst: Installation) -> bool:
        return bool(self.detect(inst.ident))


def _packages(data: object) -> Iterator[tuple[str, str | None, list[str]]]:
    """Accept JSON shapes emitted by recent pipx versions."""

    if not isinstance(data, dict):
        return
    venvs = data.get("venvs", {})
    if not isinstance(venvs, dict):
        return
    for package, value in venvs.items():
        if not isinstance(value, dict):
            continue
        metadata = value.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        main = metadata.get("main_package", {})
        if not isinstance(main, dict):
            main = {}
        real_name = str(main.get("package") or package)
        version = main.get("package_version")
        apps_value = main.get("apps", value.get("apps", []))
        apps = _app_names(apps_value)
        yield real_name, str(version) if version is not None else None, apps


def _app_names(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    names: list[str] = []
    for item in value:
        if isinstance(item, str):
            names.append(item)
        elif isinstance(item, dict) and isinstance(item.get("app"), str):
            names.append(item["app"])
    return names
