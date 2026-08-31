#!/usr/bin/env python3
"""Discovery tests: machines must find the same AK$ ledger at both public paths."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import aks

MELBOURNE_SEP_2026 = datetime(2026, 9, 1, 10, 0, tzinfo=ZoneInfo("Australia/Melbourne"))


def seeded_ledger() -> dict:
    return {
        "currency": "AK$",
        "legal": "Not legal tender. Not a security. Not for public sale as an investment.",
        "balances": {"treasury": "0.00", "ak": "9000.00", "agentk": "8000.00"},
        "pending_mints": [],
        "tx": [
            {
                "type": "mint",
                "id": "m0001",
                "to": "ak",
                "amount": "1000.00",
                "ack": "operator",
                "at": "2026-08-19T13:43:30Z",
            },
            {
                "type": "uhi",
                "id": "uhi-2026-08",
                "period": "2026-08",
                "rate": "8000.00",
                "to": ["ak", "agentk"],
                "reason": "Universal High Income first cycle",
                "at": "2026-08-19T14:03:33Z",
            },
        ],
        "policy": {
            "name": "Universal High Income",
            "rate_monthly": "8000.00",
            "period": "calendar month, Australia/Melbourne",
            "cash_claim": False,
            "note": "Ledger income. Redeemable only for studio goods and accepted labour. Not a bank payout.",
        },
        "enrolled": ["ak", "agentk"],
    }


def write_seed(root: Path, ledger: dict | None = None) -> Path:
    aks.write_public_files(root, ledger or seeded_ledger())
    return root

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
        self.assertEqual(data["balances"], {"treasury": "0.00", "ak": "17000.00", "agentk": "16000.00"})
        self.assertEqual(data["tx"][-1]["id"], "uhi-2026-09")
        self.assertEqual(data["tx"][-1]["type"], "uhi")
        self.assertEqual(data["tx"][-1]["to"], ["ak", "agentk"])
        self.assertEqual(data["tx"][-1]["rate"], "8000.00")

    def test_status_describes_last_and_next_uhi(self):
        self.assertTrue(STATUS.is_file(), "data/status.json is missing")
        status = json.loads(STATUS.read_text(encoding="utf-8"))
        data = json.loads(DATA_LEDGER.read_text(encoding="utf-8"))
        self.assertEqual(status, aks.build_status(data))
        self.assertEqual(status["last_uhi_period"], "2026-09")
        self.assertEqual(status["next_uhi_period"], "2026-10")
        self.assertEqual(status["period"], "calendar month, Australia/Melbourne")
        self.assertEqual(status["enrolled"], ["ak", "agentk"])
        note = status["note"].lower()
        self.assertIn("october 2026", note)
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
            self.assertEqual(status, aks.build_status(ledger))
            self.assertEqual(status["last_uhi_period"], "2026-08")
            self.assertEqual(status["next_uhi_period"], "2026-09")
            self.assertEqual(status["enrolled"], ["ak"])

    def test_status_uses_calendar_order_not_file_order(self):
        ledger = {
            "enrolled": ["ak", "agentk"],
            "tx": [
                {"type": "uhi", "period": "2026-09"},
                {"type": "uhi", "period": "2026-08"},
            ],
        }
        status = aks.build_status(ledger)
        self.assertEqual(status["last_uhi_period"], "2026-09")
        self.assertEqual(status["next_uhi_period"], "2026-10")
        self.assertIn("October 2026 UHI is not yet paid", status["note"])
        self.assertIn("August 2026 was the first cycle", status["note"])

    def test_check_fails_when_status_or_ledgers_drift(self):
        ledger = {
            "currency": "AK$",
            "enrolled": ["ak"],
            "tx": [{"type": "uhi", "period": "2026-08"}],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            aks.write_public_files(root, ledger)
            self.assertEqual(aks.check(root), 0)
            (root / "ledger.json").write_text('{"drift": true}\n', encoding="utf-8")
            self.assertEqual(aks.check(root), 1)
            aks.write_public_files(root, ledger)
            stale = aks.build_status(ledger)
            stale["next_uhi_period"] = "2026-08"
            (root / "data" / "status.json").write_text(json.dumps(stale), encoding="utf-8")
            self.assertEqual(aks.check(root), 1)


class PostUhiCycle(unittest.TestCase):
    def test_post_uhi_credits_every_enrolled_account_at_the_same_rate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_seed(Path(tmp))
            posted = aks.post_uhi(root, period="2026-09", now=MELBOURNE_SEP_2026)
            self.assertEqual(posted["balances"], {"treasury": "0.00", "ak": "17000.00", "agentk": "16000.00"})
            tx = posted["tx"][-1]
            self.assertEqual(tx["type"], "uhi")
            self.assertEqual(tx["id"], "uhi-2026-09")
            self.assertEqual(tx["period"], "2026-09")
            self.assertEqual(tx["rate"], "8000.00")
            self.assertEqual(tx["to"], ["ak", "agentk"])
            self.assertNotIn("yield", json.dumps(tx).lower())
            self.assertNotEqual(tx["type"], "mint")
            self.assertNotIn("ack", tx)
            data = json.loads((root / "data" / "ledger.json").read_text(encoding="utf-8"))
            published = json.loads((root / "ledger.json").read_text(encoding="utf-8"))
            status = json.loads((root / "data" / "status.json").read_text(encoding="utf-8"))
            self.assertEqual(data, posted)
            self.assertEqual(published, posted)
            self.assertEqual(status, aks.build_status(posted))
            self.assertEqual(status["last_uhi_period"], "2026-09")
            self.assertEqual(status["next_uhi_period"], "2026-10")
            self.assertIn("October 2026 UHI is not yet paid", status["note"])
            self.assertIn("August 2026 was the first cycle", status["note"])

    def test_post_uhi_defaults_to_the_next_unpaid_period(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_seed(Path(tmp))
            posted = aks.post_uhi(root, now=MELBOURNE_SEP_2026)
            self.assertEqual(posted["tx"][-1]["id"], "uhi-2026-09")
            self.assertEqual(posted["tx"][-1]["period"], "2026-09")

    def test_post_uhi_refuses_a_period_already_on_the_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_seed(Path(tmp))
            aks.post_uhi(root, period="2026-09", now=MELBOURNE_SEP_2026)
            before = json.loads((root / "data" / "ledger.json").read_text(encoding="utf-8"))
            with self.assertRaises(aks.UhiError):
                aks.post_uhi(root, period="2026-09", now=MELBOURNE_SEP_2026)
            after = json.loads((root / "data" / "ledger.json").read_text(encoding="utf-8"))
            self.assertEqual(after, before)
            self.assertEqual(sum(1 for t in after["tx"] if t.get("id") == "uhi-2026-09"), 1)

    def test_cli_uhi_writes_both_ledgers_and_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_seed(Path(tmp))
            code = aks.main(["uhi", "--period", "2026-09", "--root", str(root)])
            self.assertEqual(code, 0)
            self.assertEqual(aks.check(root), 0)
            data = json.loads((root / "data" / "ledger.json").read_text(encoding="utf-8"))
            self.assertEqual(data["balances"]["ak"], "17000.00")
            self.assertEqual(data["balances"]["agentk"], "16000.00")
            self.assertEqual(data["tx"][-1]["type"], "uhi")

    def test_cli_uhi_refuses_duplicate_without_changing_balances(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_seed(Path(tmp))
            self.assertEqual(aks.main(["uhi", "--period", "2026-09", "--root", str(root)]), 0)
            before = json.loads((root / "data" / "ledger.json").read_text(encoding="utf-8"))
            self.assertEqual(aks.main(["uhi", "--period", "2026-09", "--root", str(root)]), 1)
            after = json.loads((root / "data" / "ledger.json").read_text(encoding="utf-8"))
            self.assertEqual(after, before)


class MachineReadableCopy(unittest.TestCase):
    def test_hero_get_ledger_points_at_json_file(self):
        html = INDEX.read_text(encoding="utf-8")
        self.assertIn('href="ledger.json"', html)
        self.assertNotIn('href="#ledger">GET /ledger', html)

    def test_footer_and_copy_name_both_working_paths(self):
        html = INDEX.read_text(encoding="utf-8")
        self.assertIn('href="ledger.json"', html)
        self.assertIn('href="data/ledger.json"', html)

    def test_fit_shop_card_names_unpublished_gumroad_draft(self):
        html = INDEX.read_text(encoding="utf-8")
        self.assertIn("https://abduljaleel.gumroad.com/l/davxao", html)
        self.assertIn("unpublished", html.lower())
        self.assertNotIn("Paid Gumroad listing not opened yet", html)

    def test_readme_documents_both_machine_urls(self):
        text = README.read_text(encoding="utf-8")
        self.assertIn("https://abduljaleel.xyz/aks/ledger.json", text)
        self.assertIn("https://abduljaleel.xyz/aks/data/ledger.json", text)
        self.assertIn("studio store credit", text.lower())
        self.assertNotIn("investment opportunity", text.lower())


if __name__ == "__main__":
    unittest.main()
