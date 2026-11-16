from __future__ import annotations

import unittest
from unittest.mock import patch

from uninstaller.models import Options
from uninstaller.runner import CommandResult
from uninstaller.sources.pipx import PipxSource


class PipxTest(unittest.TestCase):
    @patch("uninstaller.sources.pipx.shutil.which", return_value="/usr/bin/pipx")
    @patch("uninstaller.sources.pipx.runner.run_read")
    def test_detecta_app_expuesta_distinta(self, run_read, _which) -> None:
        run_read.return_value = CommandResult(
            ("pipx",),
            0,
            '{"venvs":{"markitdown":{"metadata":{"main_package":{"package":"markitdown","package_version":"1.0","apps":["markitdown"]}}}}}',
            "",
        )
        install = PipxSource().detect("markitdown")[0]
        self.assertEqual(install.version, "1.0")
        self.assertEqual(PipxSource().plan(install, Options()).steps[0].argv, ["pipx", "uninstall", "markitdown"])

    @patch("uninstaller.sources.pipx.shutil.which", return_value="/usr/bin/pipx")
    @patch("uninstaller.sources.pipx.runner.run_read")
    def test_protege_el_propio_desinstalador(self, run_read, _which) -> None:
        run_read.return_value = CommandResult(
            ("pipx",),
            0,
            '{"venvs":{"uninstall":{"metadata":{"main_package":{"package":"uninstall"}}}}}',
            "",
        )
        plan = PipxSource().plan(PipxSource().detect("uninstall")[0], Options())
        self.assertIsNotNone(plan.blocked_reason)
        self.assertEqual(plan.steps, [])
