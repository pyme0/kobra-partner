from __future__ import annotations

import os
import socket
import sys
import threading
import time
import unittest
import urllib.request
from pathlib import Path

os.environ.setdefault("KOBRA_DATA_DIR", "/tmp/kobra_tests_partner_sdk")
os.environ.setdefault("KOBRA_ENV", "test")
os.environ.setdefault("KOBRA_SESSION_SECRET", "test-session-secret-largo-sdk")
os.environ.pop("KOBRA_PARTNER_KEYS_JSON", None)

_ROOT = Path(__file__).resolve().parents[3]
for p in ("control-center", "packages/kobra_core", "packages/kobra_datamap"):
    sys.path.insert(0, str(_ROOT / p))

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

TENANT = "sdk_tenant_a"
KEY = "pk_sdk_test_key_001"
TEL = "+56977776666"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


class TestKobraPartnerSdk(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import uvicorn
        from kobra_core.services.ingest_store import ingest_store
        from kobra_core.services.partner_auth import (
            DEFAULT_DATA_PLANE_SCOPES,
            partner_key_store,
        )
        import server
        from kobra_partner import AuthenticationError, Client, __version__

        partner_key_store.clear()
        partner_key_store.register(KEY, TENANT, scopes=DEFAULT_DATA_PLANE_SCOPES)
        ingest_store.delete(TENANT)

        port = _free_port()
        config = uvicorn.Config(
            server.app,
            host="127.0.0.1",
            port=port,
            log_level="error",
        )
        cls._uvi = uvicorn.Server(config)
        cls._thread = threading.Thread(target=cls._uvi.run, daemon=True)
        cls._thread.start()
        base = f"http://127.0.0.1:{port}"
        deadline = time.time() + 20
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(
                    f"{base}/api/partner/v1/openapi.json", timeout=1
                ) as r:
                    if r.status == 200:
                        break
            except Exception:
                time.sleep(0.15)
        else:
            raise RuntimeError("uvicorn no arrancó para tests del SDK")

        cls.base_url = base
        cls.client = Client(api_key=KEY, base_url=base)
        cls.Client = Client
        cls.AuthenticationError = AuthenticationError
        cls.version = __version__

    @classmethod
    def tearDownClass(cls):
        try:
            cls.client.close()
        except Exception:
            pass
        cls._uvi.should_exit = True
        cls._thread.join(timeout=5)

    def test_version_string(self):
        self.assertRegex(self.version, r"^\d+\.\d+\.\d+")

    def test_missing_key_raises_auth(self):
        bad = self.Client(api_key="not-a-real-key", base_url=self.base_url)
        try:
            with self.assertRaises(self.AuthenticationError) as ctx:
                bad.me()
            self.assertEqual(ctx.exception.status_code, 401)
        finally:
            bad.close()

    def test_me_and_sync_roundtrip(self):
        me = self.client.me()
        self.assertEqual(me["tenant_id"], TENANT)
        self.assertTrue(me.get("ok"))

        out = self.client.debtors.sync(
            [
                {
                    "external_id": "SDK-1",
                    "nombre": "Deudor SDK",
                    "telefono": TEL,
                    "lote": "Lote SDK",
                    "cuotas": [
                        {
                            "linea": "1",
                            "monto_deuda": 120000,
                            "fecha_vencimiento": "2026-08-01",
                        }
                    ],
                }
            ]
        )
        self.assertTrue(out.get("ok"))
        self.assertEqual(out.get("n_debtors"), 1)
        self.assertEqual(out.get("tenant_id"), TENANT)
        self.assertIn("panel_url", out)

        listed = self.client.debtors.list()
        self.assertEqual(listed.get("n_debtors"), 1)
        self.assertEqual(listed["debtors"][0]["external_id"], "SDK-1")

        one = self.client.debtors.get("SDK-1")
        self.assertTrue(one.get("ok"))
        self.assertEqual(one["debtor"]["nombre"], "Deudor SDK")

        summary = self.client.summary()
        self.assertIsInstance(summary, dict)
        self.assertTrue(
            summary.get("ok")
            or "cartera" in summary
            or "recaudado" in summary
            or "tenant_id" in summary
        )

        caps = self.client.capabilities()
        self.assertGreaterEqual(int(caps.get("n_leaves") or 0), 1)

        events = self.client.events.list(limit=10)
        self.assertIsInstance(events, dict)

        commitments = self.client.commitments.list(limit=10)
        self.assertIsInstance(commitments, dict)

    def test_sdk_runtime_has_no_monorepo_imports(self):
        import kobra_partner
        import kobra_partner.client as c
        import kobra_partner._http as h
        import kobra_partner.resources as r

        banned = (
            "import server",
            "from server",
            "import kobra_core",
            "from kobra_core",
            "fastapi",
            "uvicorn",
        )
        for mod in (kobra_partner, c, h, r):
            src = Path(mod.__file__).read_text(encoding="utf-8")
            for b in banned:
                self.assertNotIn(b, src, f"{mod.__file__} contains {b!r}")


if __name__ == "__main__":
    unittest.main()
