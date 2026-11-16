from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from uninstaller.models import Installation
from uninstaller.sources.manual import ManualSource


class ManualTest(unittest.TestCase):
    @patch("uninstaller.sources.manual.shutil.which")
    def test_cadena_completa_con_desktop(self, which) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            binary = home / ".local/bin/demo"
            desktop = home / ".local/share/applications/demo.desktop"
            binary.parent.mkdir(parents=True)
            desktop.parent.mkdir(parents=True)
            binary.write_text("x", encoding="utf-8")
            desktop.write_text(f"Name=Demo\nExec={binary}\n", encoding="utf-8")
            which.return_value = str(binary)
            found = ManualSource(home).detect("demo")
            self.assertEqual(found[0].paths, [binary, desktop])

    @patch("uninstaller.sources.manual.shutil.which", return_value="/no/existe/demo")
    def test_cadena_rota_no_propone(self, _which) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(ManualSource(Path(directory)).detect("demo"), [])

    def test_zed_solo_directorio_verificado(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            app = home / ".local/zed.app"
            app.mkdir(parents=True)
            found = ManualSource(home).detect("zed")
            self.assertEqual(found[0].paths, [app])
