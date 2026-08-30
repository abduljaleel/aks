#!/usr/bin/env python3
"""Discovery tests: machines must find the same AK$ ledger at both public paths."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import aks

ROOT = Path(__file__).resolve().parent
DATA_LEDGER = ROOT / "data" / "ledger.json"
ROOT_LEDGER = ROOT / "ledger.json"
STATUS = ROOT / "data" / "status.json"
INDEX = ROOT / "index.html"
README = ROOT / "README.md"


class PublishedLedgerPaths(unittest.TestCase):
    def test_root_ledger_exists_and_matches_data_ledger(self):
        self.assertTrue(DATA_LEDGER.is_file(), "canonical data/ledger.json is missing")
        self.assertTrue(
            ROOT_LEDGER.is_file(),
            "root ledger.json is missing; GitHub Pages therefore 404s /aks/ledger.json",
        )
        data = json.loads(DATA_LEDGER.read_text(encoding="utf-8"))
        root = json.loads(ROOT_LEDGER.read_text(encoding="utf-8"))
        self.assertEqual(root, data)

    def test_status_describes_last_and_next_uhi(self):
        self.assertTrue(STATUS.is_file(), "data/status.json is missing")
        status = json.loads(STATUS.read_text(encoding="utf-8"))
        self.assertEqual(status["last_uhi_period"], "2026-08")
        self.assertEqual(status["next_uhi_period"], "2026-09")
        self.assertEqual(status["period"], "calendar month, Australia/Melbourne")
        self.assertEqual(status["enrolled"], ["ak", "agentk"])
        note = status["note"].lower()
        self.assertIn("september 2026", note)
        self.assertIn("not yet paid", note)
        self.assertIn("august 2026", note)


class ClerkWritesBothLedgers(unittest.TestCase):
    def test_write_public_files_keeps_root_and_data_identical(self):
        ledger = {
            "currency": "AK$",
            "enrolled": ["ak"],
            "tx": [{"type": "uhi", "period": "2026-08"}],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").mkdir()
            aks.write_public_files(root, ledger)
            data = json.loads((root / "data" / "ledger.json").read_text(encoding="utf-8"))
            published = json.loads((root / "ledger.json").read_text(encoding="utf-8"))
            status = json.loads((root / "data" / "status.json").read_text(encoding="utf-8"))
            self.assertEqual(data, ledger)
            self.assertEqual(published, ledger)
            self.assertEqual(status["last_uhi_period"], "2026-08")
            self.assertEqual(status["next_uhi_period"], "2026-09")
            self.assertEqual(status["enrolled"], ["ak"])


class MachineReadableCopy(unittest.TestCase):
    def test_hero_get_ledger_points_at_json_file(self):
        html = INDEX.read_text(encoding="utf-8")
        self.assertIn('href="ledger.json"', html)
        self.assertNotIn('href="#ledger">GET /ledger', html)

    def test_footer_and_copy_name_both_working_paths(self):
        html = INDEX.read_text(encoding="utf-8")
        self.assertIn('href="ledger.json"', html)
        self.assertIn('href="data/ledger.json"', html)

    def test_readme_documents_both_machine_urls(self):
        text = README.read_text(encoding="utf-8")
        self.assertIn("https://abduljaleel.xyz/aks/ledger.json", text)
        self.assertIn("https://abduljaleel.xyz/aks/data/ledger.json", text)
        self.assertIn("studio store credit", text.lower())
        self.assertNotIn("investment opportunity", text.lower())


if __name__ == "__main__":
    unittest.main()
