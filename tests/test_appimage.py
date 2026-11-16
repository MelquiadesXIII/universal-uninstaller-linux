from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from uninstaller.sources.appimage import AppImageSource


class AppImageTest(unittest.TestCase):
    def test_solo_reconoce_magia_y_no_ejecuta(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            apps = home / "Applications"
            apps.mkdir()
            valid = apps / "Demo.AppImage"
            valid.write_bytes(b"x" * 8 + b"AI\x02" + b"x")
            invalid = apps / "No.AppImage"
            invalid.write_bytes(b"x" * 8 + b"NO!" + b"x")
            found = AppImageSource(home).detect("Demo")
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0].ident, str(valid))

