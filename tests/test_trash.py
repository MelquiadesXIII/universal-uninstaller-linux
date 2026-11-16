from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from uninstaller.trash import move_to_trash


class TrashTest(unittest.TestCase):
    @patch("uninstaller.trash.shutil.which", return_value=None)
    def test_mueve_y_escribe_trashinfo(self, _which) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "home"
            source = home / "Applications" / "demo"
            source.parent.mkdir(parents=True)
            source.write_text("x", encoding="utf-8")
            self.assertTrue(move_to_trash(source, home=home))
            self.assertFalse(source.exists())
            info = home / ".local/share/Trash/info/demo.trashinfo"
            self.assertTrue(info.exists())
            self.assertIn("Path=", info.read_text(encoding="utf-8"))

    @patch("uninstaller.trash.shutil.which", return_value=None)
    def test_fallo_no_hace_borrado_permanente(self, _which) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "home"
            source = home / "demo"
            home.mkdir()
            source.write_text("x", encoding="utf-8")
            with patch("uninstaller.trash.os.rename", side_effect=OSError("fallo")):
                self.assertFalse(move_to_trash(source, home=home))
            self.assertTrue(source.exists())
