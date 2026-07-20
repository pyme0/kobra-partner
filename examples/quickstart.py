from __future__ import annotations

import os
import sys

from kobra_partner import AuthenticationError, Client


def main() -> int:
    api_key = (os.environ.get("KOBRA_API_KEY") or "").strip()
    base_url = (os.environ.get("KOBRA_BASE_URL") or "").strip()
    if not api_key or not base_url:
        print("Defina KOBRA_API_KEY y KOBRA_BASE_URL", file=sys.stderr)
        return 2

    with Client(api_key=api_key, base_url=base_url) as client:
        try:
            me = client.me()
        except AuthenticationError as exc:
            print(f"Auth: {exc}", file=sys.stderr)
            return 1
        print("cuenta:", me.get("tenant_id"), "scopes:", me.get("scopes"))

        sync = client.debtors.sync(
            [
                {
                    "external_id": "DEMO-1",
                    "nombre": "Cliente Demo",
                    "telefono": "+56911112222",
                    "lote": "Demo 1",
                    "cuotas": [
                        {
                            "linea": "1",
                            "monto_deuda": 100000,
                            "fecha_vencimiento": "2026-09-01",
                        }
                    ],
                }
            ]
        )
        print("sync:", sync.get("n_debtors"), "panel:", sync.get("panel_url"))
        listed = client.debtors.list()
        print("list n:", listed.get("n_debtors"))
        print("summary keys:", sorted((client.summary() or {}).keys())[:12])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
