from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from uninstaller.executor import execute
from uninstaller.models import Installation, Plan, Step


class ExecutorTest(unittest.TestCase):
    def _plan(self, path: Path) -> Plan:
        installation = Installation("manual", "demo", "Demo", None, "user")
        return Plan(installation, [Step("trash", "Move demo", path=path)])

    @patch("uninstaller.executor.runner.run_mutating")
    def test_dry_run_no_muta(self, run) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "demo"
            path.write_text("x", encoding="utf-8")
            result = execute(self._plan(path), dry_run=True, home=Path(directory), user_roots=(Path(directory),))
            self.assertEqual(result.status, "ok")
            run.assert_not_called()
            self.assertTrue(path.exists())

    @patch("uninstaller.executor.trash.move_to_trash", return_value=True)
    def test_revalida_antes_de_borrar(self, move) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "demo"
            path.write_text("x", encoding="utf-8")
            result = execute(self._plan(path), home=Path(directory), user_roots=(Path(directory),))
            self.assertEqual(result.status, "ok")
            move.assert_called_once()

    def test_fallo_parcial(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first"
            second = root / "second"
            first.write_text("x", encoding="utf-8")
            plan = self._plan(first)
            plan.steps.append(Step("trash", "Missing", path=second))
            with patch("uninstaller.executor.trash.move_to_trash", side_effect=[True, False]):
                result = execute(plan, home=root, user_roots=(root,))
            self.assertEqual(result.status, "partial")
