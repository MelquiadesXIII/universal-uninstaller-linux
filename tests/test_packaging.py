from __future__ import annotations

import unittest
from pathlib import Path


class PackagingTest(unittest.TestCase):
    def test_install_sh_no_edita_configuracion_del_shell(self) -> None:
        script = Path("install.sh").read_text(encoding="utf-8")
        self.assertIn("python3 -m zipapp uninstaller", script)
        self.assertIn("--sources", script)
        self.assertNotIn(".bashrc", script)
        self.assertNotIn(".profile", script)
