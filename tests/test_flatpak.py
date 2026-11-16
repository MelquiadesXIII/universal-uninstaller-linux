from __future__ import annotations

import unittest
from unittest.mock import patch

from uninstaller.models import Options
from uninstaller.runner import CommandResult
from uninstaller.sources.flatpak import FlatpakSource


class FlatpakTest(unittest.TestCase):
    @patch("uninstaller.sources.flatpak.shutil.which", return_value="/usr/bin/flatpak")
    @patch("uninstaller.sources.flatpak.runner.run_read")
    def test_separa_user_y_system(self, run_read, _which) -> None:
        run_read.return_value = CommandResult(
            ("flatpak",),
            0,
            "org.demo.User\tDemo\tuser\tflathub\norg.demo.System\tDemo\tsystem\tflathub\n",
            "",
        )
        installs = FlatpakSource().detect("Demo")
        self.assertEqual([item.scope for item in installs], ["user", "system"])
        plan = FlatpakSource().plan(installs[0], Options(cleanup=True))
        self.assertEqual(plan.steps[0].argv, ["flatpak", "uninstall", "--user", "org.demo.User"])
        self.assertEqual(plan.steps[1].risk.value, "extra_confirm")

    @patch("uninstaller.sources.flatpak.shutil.which", return_value=None)
    def test_sin_flatpak_no_detecta(self, _which) -> None:
        self.assertEqual(FlatpakSource().detect("demo"), [])
