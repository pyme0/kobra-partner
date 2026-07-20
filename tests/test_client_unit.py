from __future__ import annotations

import json
import unittest

import httpx

from kobra_partner import AuthenticationError, Client, __version__


def _handler(request: httpx.Request) -> httpx.Response:
    key = request.headers.get("X-Kobra-Partner-Key", "")
    path = request.url.path

    if key != "pk_good":
        return httpx.Response(401, json={"detail": "partner key inválida o ausente"})

    if path.endswith("/me") and request.method == "GET":
        return httpx.Response(
            200,
            json={
                "ok": True,
                "tenant_id": "acme",
                "scopes": ["debtors:read", "debtors:write"],
                "key_id": "k1",
            },
        )

    if path.endswith("/debtors/sync") and request.method == "POST":
        body = json.loads(request.content.decode("utf-8"))
        n = len(body.get("debtors") or body.get("deudores") or [])
        return httpx.Response(
            201,
            json={
                "ok": True,
                "tenant_id": "acme",
                "n_debtors": n,
                "panel_url": "/clientes?tenant=acme",
            },
        )

    if path.endswith("/debtors") and request.method == "GET":
        return httpx.Response(
            200,
            json={
                "ok": True,
                "tenant_id": "acme",
                "n_debtors": 1,
                "debtors": [{"external_id": "X-1", "nombre": "Ada"}],
            },
        )

    if "/debtors/" in path and request.method == "GET":
        return httpx.Response(
            200,
            json={"ok": True, "debtor": {"external_id": "X-1", "nombre": "Ada"}},
        )

    if path.endswith("/summary"):
        return httpx.Response(200, json={"ok": True, "recaudado": {"total": 0}})

    if path.endswith("/sdk-map"):
        return httpx.Response(200, json={"ok": True, "n_leaves": 27, "leaves": []})

    if path.endswith("/events"):
        return httpx.Response(200, json={"ok": True, "items": []})

    if path.endswith("/commitments"):
        return httpx.Response(200, json={"ok": True, "n": 0, "items": []})

    if path.endswith("/payments") and request.method == "POST":
        return httpx.Response(200, json={"ok": True, "tenant_id": "acme"})

    if path.endswith("/cases"):
        return httpx.Response(200, json={"ok": True, "exists": False})

    return httpx.Response(404, json={"detail": "not found"})


class TestClientUnit(unittest.TestCase):
    def setUp(self):
        transport = httpx.MockTransport(_handler)
        self.client = Client(
            api_key="pk_good",
            base_url="https://example.test",
            transport=transport,
        )

    def tearDown(self):
        self.client.close()

    def test_version(self):
        self.assertEqual(__version__, "0.1.0")

    def test_auth_header_and_me(self):
        me = self.client.me()
        self.assertEqual(me["tenant_id"], "acme")

    def test_bad_key(self):
        bad = Client(
            api_key="pk_bad",
            base_url="https://example.test",
            transport=httpx.MockTransport(_handler),
        )
        try:
            with self.assertRaises(AuthenticationError) as ctx:
                bad.me()
            self.assertEqual(ctx.exception.status_code, 401)
        finally:
            bad.close()

    def test_sync_list_get(self):
        out = self.client.debtors.sync(
            [{"external_id": "X-1", "nombre": "Ada", "cuotas": []}]
        )
        self.assertEqual(out["n_debtors"], 1)
        listed = self.client.debtors.list()
        self.assertEqual(listed["n_debtors"], 1)
        one = self.client.debtors.get("X-1")
        self.assertEqual(one["debtor"]["nombre"], "Ada")

    def test_other_resources(self):
        self.assertTrue(self.client.summary().get("ok"))
        self.assertEqual(self.client.capabilities()["n_leaves"], 27)
        self.assertIn("items", self.client.events.list())
        self.assertIn("items", self.client.commitments.list())
        self.assertTrue(
            self.client.payments.register(
                amount=1, external_id="X-1", nombre="Ada"
            ).get("ok")
        )
        self.assertFalse(self.client.cases.get(external_id="X-1").get("exists"))


if __name__ == "__main__":
    unittest.main()
