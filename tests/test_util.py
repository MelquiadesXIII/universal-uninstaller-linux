from __future__ import annotations

import unittest
from pathlib import Path

from uninstaller.util import has_parent_component, parse_desktop, valid_term


class UtilTest(unittest.TestCase):
    def test_parsea_exec_con_env_comillas_y_codigos(self) -> None:
        entry = parse_desktop(
            'Name=Demo\nExec=env QT_QPA_PLATFORM=x11 "/opt/Demo App/demo" %U\nIcon=demo\n'
        )
        self.assertEqual(entry.name, "Demo")
        self.assertEqual(entry.exec_argv, ("/opt/Demo App/demo",))
        self.assertEqual(entry.icon, "demo")

    def test_rechaza_terminos_inseguros(self) -> None:
        for value in ("", "-rf", "a;b", "$(x)", "a b"):
            self.assertFalse(valid_term(value))

    def test_acepta_termino_normal(self) -> None:
        self.assertTrue(valid_term("wine32:i386"))
        self.assertTrue(has_parent_component(Path("a/../b")))
