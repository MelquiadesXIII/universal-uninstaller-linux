"""Detection of manual installations with complete evidence chains."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from .. import runner
from ..models import Evidence, Installation, Options, Plan, Risk, Step
from ..util import parse_desktop


class ManualSource:
    """Only propose concrete files with a complete evidence chain."""

    name = "manual"

    def __init__(self, home: Path | None = None) -> None:
        self.home = (home or Path.home()).expanduser()

    def available(self) -> bool:
        return True

    def detect(self, term: str) -> list[Installation]:
        if term == "brew" or term == "homebrew":
            return []
        if term == "ollama":
            return self._detect_ollama()
        if term == "zed":
            return self._detect_directory_app("zed", self.home / ".local/zed.app")
        if term == "opencode":
            return self._detect_directory_app("opencode", self.home / ".opencode")
        executable = shutil.which(term)
        if executable is None:
            return []
        resolved = Path(os.path.realpath(executable))
        desktops = self._desktops_for(resolved)
        if not desktops:
            return []
        paths = [Path(executable), *desktops]
        evidence = [Evidence("path", f"{executable} -> {resolved}", 3)]
        evidence.extend(Evidence("desktop", str(desktop), 3) for desktop in desktops)
        return [
            Installation(self.name, term, term, None, "user" if resolved.is_relative_to(self.home) else "system", paths=paths, evidence=evidence)
        ]

    def plan(self, inst: Installation, opts: Options) -> Plan:
        steps = [
            Step(
                "trash" if not path.is_absolute() or path.is_relative_to(self.home) else "root_rm",
                f"Remove {path}",
                path=path,
                needs_root=not path.is_relative_to(self.home),
                risk=Risk.EXTRA_CONFIRM if inst.ident == "ollama" else Risk.NORMAL,
            )
            for path in inst.paths
        ]
        warnings: list[str] = []
        if inst.ident == "ollama":
            steps = [
                Step("run", "Stop ollama.service", ["sudo", "systemctl", "stop", "--", "ollama.service"], needs_root=True, risk=Risk.EXTRA_CONFIRM),
                Step("run", "Disable ollama.service", ["sudo", "systemctl", "disable", "--", "ollama.service"], needs_root=True, risk=Risk.EXTRA_CONFIRM),
                *steps,
            ]
            warnings.append("Ollama models and the system user are preserved.")
        return Plan(inst, steps=steps, warnings=warnings)

    def verify(self, inst: Installation) -> bool:
        return bool(self.detect(inst.ident))

    def _detect_directory_app(self, ident: str, directory: Path) -> list[Installation]:
        link = self.home / ".local/bin" / ident
        if not directory.is_dir():
            return []
        paths = [directory]
        if link.is_symlink() and Path(os.path.realpath(link)).is_relative_to(directory):
            paths.insert(0, link)
        return [
            Installation(
                self.name,
                ident,
                ident,
                None,
                "user",
                paths=paths,
                evidence=[Evidence("path", str(path), 3) for path in paths],
            )
        ]

    def _detect_ollama(self) -> list[Installation]:
        binary = Path("/usr/local/bin/ollama")
        if not binary.is_file():
            return []
        service = runner.run_read(["systemctl", "cat", "ollama.service"])
        paths = [binary]
        if service.returncode == 0:
            paths.append(Path("/etc/systemd/system/ollama.service"))
        return [
            Installation(
                self.name,
                "ollama",
                "ollama",
                None,
                "system",
                paths=paths,
                evidence=[Evidence("path", str(binary), 3), Evidence("systemd", "ollama.service", 2)],
                extras={"model_path": Path("/usr/share/ollama")},
            )
        ]

    def _desktops_for(self, executable: Path) -> list[Path]:
        found: list[Path] = []
        for directory in (self.home / ".local/share/applications", Path("/usr/share/applications")):
            if not directory.is_dir():
                continue
            for desktop in directory.glob("*.desktop"):
                try:
                    entry = parse_desktop(desktop.read_text(encoding="utf-8", errors="replace"))
                except OSError:
                    continue
                if entry.exec_argv and Path(entry.exec_argv[0]).expanduser() == executable:
                    found.append(desktop)
        return found
