from __future__ import annotations

import os
import sys
from typing import Any

from kobra_partner import Client

REQUIRED_METHODS = (
    "me",
    "summary",
    "capabilities",
    "debtors.sync",
    "debtors.list",
    "debtors.get",
    "cases.get",
    "commitments.list",
    "payments.register",
    "events.list",
)

SAMPLE_DEBTOR = {
    "external_id": "EX-100",
    "nombre": "María Ejemplo",
    "telefono": "+56987654321",
    "lote": "Lote 1",
    "cuotas": [
        {
            "linea": "1",
            "monto_deuda": 150000,
            "fecha_vencimiento": "2026-08-01",
        }
    ],
}


def run_full_surface(client: Client) -> dict[str, Any]:
    exercised: list[str] = []
    out: dict[str, Any] = {}

    out["me"] = client.me()
    exercised.append("me")

    out["summary"] = client.summary()
    exercised.append("summary")

    out["capabilities"] = client.capabilities()
    exercised.append("capabilities")

    out["debtors.sync"] = client.debtors.sync([SAMPLE_DEBTOR])
    exercised.append("debtors.sync")

    out["debtors.list"] = client.debtors.list()
    exercised.append("debtors.list")

    out["debtors.get"] = client.debtors.get("EX-100")
    exercised.append("debtors.get")

    out["cases.get"] = client.cases.get(external_id="EX-100")
    exercised.append("cases.get")

    out["commitments.list"] = client.commitments.list(limit=20)
    exercised.append("commitments.list")

    out["payments.register"] = client.payments.register(
        amount=150000,
        external_id="EX-100",
        nombre="María Ejemplo",
        telefono="+56987654321",
        paid_at="2026-07-20",
        external_ref="demo-pago-1",
    )
    exercised.append("payments.register")

    out["events.list"] = client.events.list(limit=20)
    exercised.append("events.list")

    missing = [m for m in REQUIRED_METHODS if m not in exercised]
    return {
        "exercised": exercised,
        "missing": missing,
        "complete": not missing,
        "results": out,
    }


def main() -> int:
    api_key = (os.environ.get("KOBRA_API_KEY") or "").strip()
    base_url = (os.environ.get("KOBRA_BASE_URL") or "").strip()
    if not api_key or not base_url:
        print(
            "Defina KOBRA_API_KEY y KOBRA_BASE_URL para el ejemplo en vivo.",
            file=sys.stderr,
        )
        return 2

    with Client(api_key=api_key, base_url=base_url) as client:
        report = run_full_surface(client)
    print("complete=", report["complete"])
    print("exercised=", report["exercised"])
    if report["missing"]:
        print("missing=", report["missing"], file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
