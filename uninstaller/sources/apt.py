"""Detection and planning for APT/dpkg packages."""

from __future__ import annotations

import fnmatch
import shutil
from dataclasses import dataclass

from .. import runner
from ..config import APT_SUITES
from ..models import Evidence, Installation, Options, Plan, Risk, Step
from ..safety import critical_level, simulation_criticals

DPKG_QUERY = (
    "dpkg-query",
    "-W",
    "-f=${binary:Package}\\t${Version}\\t${db:Status-Abbrev}\\t"
    "${Essential}\\t${Protected}\\n",
)


@dataclass(frozen=True)
class DpkgPackage:
    name: str
    version: str
    status: str
    essential: bool
    protected: bool

    @property
    def residual(self) -> bool:
        return self.status.startswith("rc")


def parse_dpkg_query(text: str) -> list[DpkgPackage]:
    """Parse tab-separated dpkg-query output."""

    packages: list[DpkgPackage] = []
    for line in text.splitlines():
        fields = line.split("\t")
        if len(fields) != 5:
            continue
        name, version, status, essential, protected = fields
        packages.append(
            DpkgPackage(
                name,
                version,
                status,
                essential.lower() == "yes",
                protected.lower() == "yes",
            )
        )
    return packages


class AptSource:
    """Source based on the dpkg inventory and apt-get operations."""

    name = "apt"

    def available(self) -> bool:
        return shutil.which("dpkg-query") is not None and shutil.which("apt-get") is not None

    def detect(self, term: str) -> list[Installation]:
        if not self.available():
            return []
        result = runner.run_read(DPKG_QUERY)
        if result.returncode != 0:
            return []
        packages = parse_dpkg_query(result.stdout)
        selected = self._select(term, packages)
        if not selected:
            return []
        suite = term if term in APT_SUITES else None
        ident = suite or selected[0].name
        display = f"{ident} (suite)" if suite else selected[0].name
        return [
            Installation(
                source=self.name,
                ident=ident,
                display_name=display,
                version=None if suite else selected[0].version,
                scope="system",
                packages=[package.name for package in selected],
                evidence=[
                    Evidence("dpkg", f"{package.name} {package.version}", 3)
                    for package in selected
                ],
                state="residual" if all(package.residual for package in selected) else "installed",
                extras={"dpkg": selected},
            )
        ]

    def plan(self, inst: Installation, opts: Options) -> Plan:
        if inst.state == "residual":
            if opts.purge:
                return Plan(
                    inst,
                    steps=[
                        Step(
                            "run",
                            f"Purge APT configuration: {' '.join(inst.packages)}",
                            argv=[
                                "sudo",
                                "apt-get",
                                "purge",
                                *(["-y"] if opts.yes else []),
                                "--",
                                *inst.packages,
                            ],
                            needs_root=True,
                            risk=Risk.EXTRA_CONFIRM,
                        )
                    ],
                    warnings=[
                        f"{inst.ident} is already uninstalled; its configuration files will be removed."
                    ],
                )
            return Plan(
                inst,
                warnings=[
                    f"{inst.ident} is already uninstalled; only configuration files remain."
                ],
            )
        simulation = runner.run_read(["apt-get", "-s", "remove", "--", *inst.packages])
        removed = _removed_packages(simulation.stdout)
        criticals = simulation_criticals(simulation.stdout)
        unexpected = [name for name in removed if name not in inst.packages]
        if criticals:
            return Plan(
                inst,
                warnings=[f"APT would remove critical packages: {', '.join(criticals)}"],
                blocked_reason="The APT simulation includes critical packages.",
            )
        risk = Risk.EXTRA_CONFIRM if len(unexpected) > 5 else Risk.NORMAL
        steps = [
            Step(
                "run",
                f"Remove APT packages: {' '.join(inst.packages)}",
                argv=["sudo", "apt-get", "remove", *(["-y"] if opts.yes else []), "--", *inst.packages],
                needs_root=True,
                risk=risk,
            )
        ]
        warnings = []
        if unexpected:
            warnings.append(f"Additional packages in simulation: {', '.join(unexpected)}")
        if opts.purge:
            steps.append(
                Step(
                    "run",
                    f"Purge configuration for: {' '.join(inst.packages)}",
                    argv=["sudo", "apt-get", "purge", "--", *inst.packages],
                    needs_root=True,
                    risk=Risk.EXTRA_CONFIRM,
                )
            )
        return Plan(inst, steps=steps, warnings=warnings)

    def verify(self, inst: Installation) -> bool:
        return bool(self.detect(inst.ident))

    @staticmethod
    def _select(term: str, packages: list[DpkgPackage]) -> list[DpkgPackage]:
        if term in APT_SUITES:
            patterns = APT_SUITES[term]
            return [package for package in packages if any(fnmatch.fnmatch(package.name, pattern) for pattern in patterns)]
        return [package for package in packages if package.name == term]


def _removed_packages(text: str) -> list[str]:
    """Return package names from `Remv` lines in a simulation."""

    return [fields[1] for fields in (line.split() for line in text.splitlines()) if len(fields) >= 2 and fields[0] == "Remv"]
