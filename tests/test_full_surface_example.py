from __future__ import annotations

import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "examples"))

from full_surface import REQUIRED_METHODS, run_full_surface
from mock_partner import make_mock_transport
from kobra_partner import Client


class TestFullSurfaceExample(unittest.TestCase):
    def test_all_public_client_methods_via_package(self):
        transport = make_mock_transport(api_key="pk_demo")
        with Client(
            api_key="pk_demo",
            base_url="https://example.test",
            transport=transport,
        ) as client:
            report = run_full_surface(client)

        self.assertTrue(report["complete"], report["missing"])
        self.assertEqual(list(report["exercised"]), list(REQUIRED_METHODS))
        for name in REQUIRED_METHODS:
            self.assertIn(name, report["results"])
            self.assertIsInstance(report["results"][name], dict)

        me = report["results"]["me"]
        self.assertEqual(me.get("tenant_id"), "demo")
        sync = report["results"]["debtors.sync"]
        self.assertEqual(sync.get("n_debtors"), 1)
        listed = report["results"]["debtors.list"]
        self.assertEqual(listed.get("n_debtors"), 1)
        one = report["results"]["debtors.get"]
        self.assertEqual(one["debtor"]["external_id"], "EX-100")
        pay = report["results"]["payments.register"]
        self.assertTrue(pay.get("ok"))
        events = report["results"]["events.list"]
        self.assertGreaterEqual(int(events.get("n") or len(events.get("items") or [])), 1)

    def test_example_modules_do_not_import_monorepo(self):
        for rel in ("examples/full_surface.py", "examples/mock_partner.py"):
            src = (_ROOT / rel).read_text(encoding="utf-8")
            for banned in (
                "import server",
                "from server",
                "kobra_core",
                "control-center",
                "uvicorn",
                "fastapi",
            ):
                self.assertNotIn(banned, src, f"{rel} contains {banned!r}")


if __name__ == "__main__":
    unittest.main()
