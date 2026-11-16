from __future__ import annotations

import unittest
from unittest.mock import patch

from uninstaller.cli import main
from uninstaller.models import Installation, Plan, Step
from uninstaller.orchestrator import Orchestrator


class IntegrationTest(unittest.TestCase):
    def test_plan_completo_no_ejecuta_runner(self) -> None:
        class Source:
            name = "fake"

            def available(self):
                return True

            def detect(self, term):
                return [Installation("fake", "demo", "Demo", "1", "user")]

            def plan(self, inst, options):
                return Plan(inst, [Step("info", "Information only")])

            def verify(self, inst):
                return True

        orchestrator = Orchestrator([Source()])
        with patch("uninstaller.executor.runner.run_mutating") as mutate:
            self.assertEqual(main(["--dry-run", "demo"], orchestrator=orchestrator), 0)
            mutate.assert_not_called()

    def test_codigos_de_uso_y_root(self) -> None:
        orchestrator = Orchestrator([])
        self.assertEqual(main([], orchestrator=orchestrator), 2)
        with patch("uninstaller.cli.os.geteuid", return_value=0):
            self.assertEqual(main(["demo"], orchestrator=orchestrator), 2)
