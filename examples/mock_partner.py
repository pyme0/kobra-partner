from __future__ import annotations

import json
from typing import Any

import httpx

API = "/api/partner/v1"


def make_mock_transport(*, api_key: str = "pk_demo") -> httpx.MockTransport:
    state: dict[str, Any] = {
        "debtors": [],
        "payments": [],
        "events": [],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        key = request.headers.get("X-Kobra-Partner-Key", "")
        if key != api_key:
            return httpx.Response(401, json={"detail": "partner key inválida o ausente"})

        path = request.url.path
        method = request.method.upper()
        if not path.startswith(API):
            return httpx.Response(404, json={"detail": "not found"})
        sub = path[len(API) :] or "/"

        if method == "GET" and sub == "/me":
            return httpx.Response(
                200,
                json={
                    "ok": True,
                    "tenant_id": "demo",
                    "scopes": ["debtors:read", "debtors:write", "payments:write"],
                    "key_id": "k1",
                },
            )

        if method == "GET" and sub == "/summary":
            return httpx.Response(
                200,
                json={
                    "ok": True,
                    "tenant_id": "demo",
                    "recaudado": {"mes": 0, "mes_anterior": 0, "total": 0},
                    "cartera": {"n_debtors": len(state["debtors"])},
                },
            )

        if method == "GET" and sub == "/sdk-map":
            return httpx.Response(
                200,
                json={"ok": True, "n_leaves": 27, "leaves": [], "tenant_id": "demo"},
            )

        if method == "POST" and sub == "/debtors/sync":
            body = json.loads(request.content.decode("utf-8") or "{}")
            rows = body.get("debtors") or body.get("deudores") or []
            state["debtors"] = list(rows)
            return httpx.Response(
                201,
                json={
                    "ok": True,
                    "tenant_id": "demo",
                    "n_debtors": len(state["debtors"]),
                    "panel_url": "/clientes?tenant=demo",
                },
            )

        if method == "GET" and sub == "/debtors":
            return httpx.Response(
                200,
                json={
                    "ok": True,
                    "tenant_id": "demo",
                    "n_debtors": len(state["debtors"]),
                    "debtors": state["debtors"],
                },
            )

        if method == "GET" and sub.startswith("/debtors/"):
            ref = sub.split("/", 2)[-1]
            for d in state["debtors"]:
                if str(d.get("external_id") or "") == ref or str(d.get("nombre") or "") == ref:
                    return httpx.Response(
                        200, json={"ok": True, "tenant_id": "demo", "debtor": d}
                    )
            return httpx.Response(404, json={"detail": "deudor no encontrado"})

        if method == "GET" and sub == "/cases":
            return httpx.Response(
                200,
                json={
                    "ok": True,
                    "exists": True,
                    "tenant_id": "demo",
                    "case": {"case_id": "c1", "status": "OPEN"},
                    "compromisos": [],
                    "pagos": state["payments"],
                    "eventos": state["events"],
                },
            )

        if method == "GET" and sub == "/commitments":
            return httpx.Response(
                200, json={"ok": True, "tenant_id": "demo", "n": 0, "items": []}
            )

        if method == "POST" and sub == "/payments":
            body = json.loads(request.content.decode("utf-8") or "{}")
            state["payments"].append(body)
            state["events"].append({"type": "PAYMENT_CONFIRMED", "amount": body.get("amount")})
            return httpx.Response(
                200, json={"ok": True, "tenant_id": "demo", "registered": True}
            )

        if method == "GET" and sub == "/events":
            return httpx.Response(
                200,
                json={
                    "ok": True,
                    "tenant_id": "demo",
                    "items": state["events"],
                    "n": len(state["events"]),
                },
            )

        return httpx.Response(404, json={"detail": f"mock no implementa {method} {sub}"})

    return httpx.MockTransport(handler)
