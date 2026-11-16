from __future__ import annotations

import unittest
from unittest.mock import patch

from uninstaller.runner import run_mutating, run_read


class RunnerTest(unittest.TestCase):
    @patch("uninstaller.runner.subprocess.run")
    def test_lectura_fija_lc_all_y_captura(self, run) -> None:
        run.return_value.returncode = 0
        run.return_value.stdout = "output"
        run.return_value.stderr = ""
        result = run_read(["dpkg-query", "--version"])
        self.assertEqual(result.stdout, "output")
        kwargs = run.call_args.kwargs
        self.assertEqual(kwargs["env"]["LC_ALL"], "C")
        self.assertTrue(kwargs["capture_output"])

    @patch("uninstaller.runner.subprocess.run")
    def test_mutacion_hereda_terminal(self, run) -> None:
        run.return_value.returncode = 7
        self.assertEqual(run_mutating(["echo", "ok"]), 7)
        self.assertFalse(run.call_args.kwargs.get("capture_output", False))

    @patch("uninstaller.runner.subprocess.run")
    def test_validate_sudo_usa_codigo_de_retorno(self, run) -> None:
        run.return_value.returncode = 0
        from uninstaller.runner import validate_sudo

        self.assertEqual(validate_sudo(), 0)
        self.assertEqual(run.call_args.args[0], ["sudo", "-v"])
