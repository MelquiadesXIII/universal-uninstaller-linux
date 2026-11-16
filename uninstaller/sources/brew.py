"""Homebrew source with explicit protection for the package manager itself."""

from __future__ import annotations

import shutil
from pathlib import Path

from .. import runner
from ..models import Evidence, Installation, Options, Plan, Risk, Step


class BrewSource:
    """Detect formulas and casks without forcing removals."""

    name = "brew"

    def available(self) -> bool:
        return self._brew() is not None

    def detect(self, term: str) -> list[Installation]:
        brew = self._brew()
        if brew is None:
            return []
        if term.casefold() in {"brew", "homebrew"}:
            return [
                Installation(
                    self.name,
                    "brew",
                    "Homebrew",
                    None,
                    "user",
                    evidence=[Evidence("brew", str(brew), 3)],
                )
            ]
        matches: list[Installation] = []
        for kind in ("formula", "cask"):
            result = runner.run_read([str(brew), "list", f"--{kind}"])
            if result.returncode != 0:
                continue
            for name in result.stdout.splitlines():
                if name.strip().casefold() != term.casefold():
                    continue
                dependents = self._dependents(brew, name)
                matches.append(
                    Installation(
                        self.name,
                        name.strip(),
                        name.strip(),
                        None,
                        "user",
                        evidence=[Evidence("brew", f"{kind}: {name.strip()}", 3)],
                        extras={"kind": kind, "dependents": dependents, "brew_path": str(brew)},
                    )
                )
        return matches

    def plan(self, inst: Installation, opts: Options) -> Plan:
        if inst.ident in {"brew", "homebrew"}:
            return Plan(
                inst,
                warnings=["Homebrew is preserved. Consult the official instructions to remove it."],
                blocked_reason="Homebrew is protected and produces no executable steps.",
            )
        dependents = inst.extras.get("dependents", [])
        if dependents:
            return Plan(
                inst,
                warnings=[f"Installed dependents: {', '.join(str(item) for item in dependents)}"],
                blocked_reason="The package cannot be uninstalled while dependents exist.",
            )
        brew = Path(inst.extras["brew_path"]) if inst.extras.get("brew_path") else self._brew()
        if brew is None:
            return Plan(inst, blocked_reason="Homebrew is no longer available.")
        steps = [
            Step(
                "run",
                f"Uninstall Homebrew package {inst.ident}",
                argv=[str(brew), "uninstall", inst.ident],
            )
        ]
        warnings: list[str] = []
        if opts.cleanup:
            help_result = runner.run_read([str(brew), "autoremove", "--help"])
            if help_result.returncode == 0:
                steps.append(
                    Step(
                        "run",
                        "Clean up orphaned Homebrew dependencies",
                        argv=[str(brew), "autoremove", "--dry-run"],
                        risk=Risk.EXTRA_CONFIRM,
                    )
                )
            else:
                warnings.append("This Homebrew version does not provide autoremove.")
        return Plan(inst, steps=steps, warnings=warnings)

    def verify(self, inst: Installation) -> bool:
        return bool(self.detect(inst.ident))

    def _brew(self) -> Path | None:
        candidate = shutil.which("brew")
        if candidate is None:
            for known in (Path.home() / ".linuxbrew/bin/brew", Path("/home/linuxbrew/.linuxbrew/bin/brew")):
                if known.is_file():
                    candidate = str(known)
                    break
        if candidate is None:
            return None
        result = runner.run_read([candidate, "--prefix"])
        return Path(candidate) if result.returncode == 0 else None

    @staticmethod
    def _dependents(brew: Path, name: str) -> list[str]:
        result = runner.run_read([str(brew), "uses", "--installed", name])
        if result.returncode != 0:
            return []
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
