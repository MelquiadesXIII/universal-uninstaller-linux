from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from uninstaller.safety import critical_level, simulation_criticals, validate_path


class SafetyTest(unittest.TestCase):
    def test_capas_de_criticos(self) -> None:
        self.assertEqual(critical_level("dolphin"), "blocked")
        self.assertEqual(critical_level("curl"), "extra_confirm")
        self.assertEqual(critical_level("demo"), "normal")
        self.assertEqual(critical_level("demo", essential=True), "blocked")

    def test_detecta_criticos_en_simulacion(self) -> None:
        self.assertEqual(simulation_criticals("Remv dolphin (1.0)\nRemv demo (1.0)"), ["dolphin"])

    def test_rechaza_ruta_fuera_de_raiz_y_acepta_hija(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            child = root / "app"
            child.write_text("x", encoding="utf-8")
            self.assertEqual(validate_path(child, home=root, roots=(root,))[0], True)
            self.assertFalse(validate_path(Path("/"), home=root, roots=(root,))[0])
