from __future__ import annotations

import unittest
from unittest.mock import patch

from uninstaller.cli import main
from uninstaller.models import Installation
from uninstaller.orchestrator import Orchestrator


class FakeSource:
    def __init__(self, candidates, name="fake") -> None:
        self.name = name
        self.candidates = candidates

    def available(self) -> bool:
        return True

    def detect(self, term):
        return self.candidates

    def plan(self, inst, options):
        from uninstaller.models import Plan

        return Plan(inst)

    def verify(self, inst):
        return True


class OrchestratorCliTest(unittest.TestCase):
    def test_dolphin_ambiguo(self) -> None:
        candidates = [
            Installation("apt", "dolphin", "Dolphin KDE", None, "system"),
            Installation("appimage", "/tmp/dolphin", "Dolphin Emulator", None, "user"),
        ]
        resolution = Orchestrator(
            [FakeSource([candidates[0]], "apt"), FakeSource([candidates[1]], "appimage")]
        ).resolve("dolphin", tty=False)
        self.assertEqual(resolution.status, "ambiguous")

    def test_dolphin_emu_es_nombre_canonico(self) -> None:
        candidate = Installation("appimage", "/tmp/Dolphin_Emulator.AppImage", "Dolphin Emulator", None, "user")
        resolution = Orchestrator([FakeSource([candidate], "appimage")]).resolve("dolphin-emu", tty=False)
        self.assertEqual(resolution.status, "ok")
        self.assertEqual(resolution.candidates[0].display_name, "Dolphin Emulator")

    def test_cli_no_encontrada(self) -> None:
        orchestrator = Orchestrator([FakeSource([])])
        with patch("uninstaller.cli.os.geteuid", return_value=1000):
            self.assertEqual(main(["demo"], orchestrator=orchestrator), 3)

    @patch("uninstaller.cli.os.geteuid", return_value=1000, create=True)
    def test_cli_dry_run(self, _geteuid) -> None:
        candidate = Installation("fake", "demo", "Demo", None, "user")
        self.assertEqual(main(["--dry-run", "demo"], orchestrator=Orchestrator([FakeSource([candidate])])), 0)
