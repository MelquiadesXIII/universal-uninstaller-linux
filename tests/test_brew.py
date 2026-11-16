from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from uninstaller.models import Options
from uninstaller.runner import CommandResult
from uninstaller.sources.brew import BrewSource


class BrewTest(unittest.TestCase):
    @patch("uninstaller.sources.brew.runner.run_read")
    @patch("uninstaller.sources.brew.shutil.which", return_value="/home/linuxbrew/bin/brew")
    def test_dependiente_bloquea(self, which, run_read) -> None:
        run_read.side_effect = [
            CommandResult(("brew",), 0, "/home/linuxbrew\n", ""),
            CommandResult(("brew",), 0, "demo\n", ""),
            CommandResult(("brew",), 0, "other\n", ""),
            CommandResult(("brew",), 0, "", ""),
        ]
        install = BrewSource().detect("demo")[0]
        plan = BrewSource().plan(install, Options())
        self.assertIsNotNone(plan.blocked_reason)

    @patch("uninstaller.sources.brew.runner.run_read")
    @patch("uninstaller.sources.brew.shutil.which", return_value="/home/linuxbrew/bin/brew")
    def test_homebrew_no_genera_step(self, which, run_read) -> None:
        run_read.return_value = CommandResult(("brew",), 0, "/home/linuxbrew\n", "")
        install = BrewSource().detect("brew")[0]
        plan = BrewSource().plan(install, Options())
        self.assertEqual(plan.steps, [])
        self.assertIsNotNone(plan.blocked_reason)

    @patch("uninstaller.sources.brew.runner.run_read")
    @patch("uninstaller.sources.brew.shutil.which", return_value="/home/linuxbrew/bin/brew")
    def test_autoremove_solo_si_help_funciona(self, which, run_read) -> None:
        run_read.side_effect = [
            CommandResult(("brew",), 0, "/home/linuxbrew\n", ""),
            CommandResult(("brew",), 0, "demo\n", ""),
            CommandResult(("brew",), 0, "", ""),
            CommandResult(("brew",), 0, "", ""),
            CommandResult(("brew",), 0, "usage\n", ""),
        ]
        install = BrewSource().detect("demo")[0]
        plan = BrewSource().plan(install, Options(cleanup=True))
        self.assertEqual(plan.steps[-1].argv, ["/home/linuxbrew/bin/brew", "autoremove", "--dry-run"])
