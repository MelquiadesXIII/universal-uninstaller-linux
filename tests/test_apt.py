from __future__ import annotations

import unittest
from unittest.mock import patch

from uninstaller.models import Options, Risk
from uninstaller.runner import CommandResult
from uninstaller.sources.apt import AptSource, parse_dpkg_query


class AptTest(unittest.TestCase):
    def test_parsea_estado_rc_y_campos_de_seguridad(self) -> None:
        packages = parse_dpkg_query("wine32:i386\t1.0\trc\tno\tno\nsudo\t2\tii \tyes\tyes\n")
        self.assertTrue(packages[0].residual)
        self.assertTrue(packages[1].essential)
        self.assertTrue(packages[1].protected)

    @patch("uninstaller.sources.apt.shutil.which", return_value="/usr/bin/tool")
    @patch("uninstaller.sources.apt.runner.run_read")
    def test_suite_wine_incluye_arquitectura(self, run_read, _which) -> None:
        run_read.return_value = CommandResult(
            ("dpkg-query",),
            0,
            "wine\t1\tii \tno\tno\nwine32:i386\t1\tii \tno\tno\nlibwine9\t1\tii \tno\tno\n",
            "",
        )
        installations = AptSource().detect("wine")
        self.assertEqual(installations[0].packages, ["wine", "wine32:i386", "libwine9"])

    @patch("uninstaller.sources.apt.runner.run_read")
    def test_simulacion_critica_bloquea(self, run_read) -> None:
        run_read.return_value = CommandResult(("apt-get",), 0, "Remv dolphin (1)\n", "")
        from uninstaller.models import Evidence, Installation

        inst = Installation("apt", "demo", "demo", None, "system", ["demo"], evidence=[Evidence("dpkg", "demo", 3)])
        plan = AptSource().plan(inst, Options())
        self.assertIsNotNone(plan.blocked_reason)

    def test_residual_no_genera_pasos_de_desinstalacion(self) -> None:
        from uninstaller.models import Installation

        inst = Installation(
            "apt",
            "psiphonlinuxgui",
            "psiphonlinuxgui",
            "1.5.0",
            "system",
            ["psiphonlinuxgui"],
            state="residual",
        )
        plan = AptSource().plan(inst, Options())
        self.assertEqual(plan.steps, [])
        self.assertIn("already uninstalled", plan.warnings[0])

    def test_residual_con_purge_genera_solo_purga(self) -> None:
        from uninstaller.models import Installation

        inst = Installation(
            "apt",
            "psiphonlinuxgui",
            "psiphonlinuxgui",
            "1.5.0",
            "system",
            ["psiphonlinuxgui"],
            state="residual",
        )
        plan = AptSource().plan(inst, Options(purge=True, yes=True))
        self.assertEqual(
            plan.steps[0].argv,
            ["sudo", "apt-get", "purge", "-y", "--", "psiphonlinuxgui"],
        )
        self.assertEqual(plan.steps[0].risk, Risk.EXTRA_CONFIRM)
