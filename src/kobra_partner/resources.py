from __future__ import annotations

from typing import Any, Mapping, Sequence

from kobra_partner._http import HttpTransport


class DebtorsResource:
    def __init__(self, http: HttpTransport) -> None:
        self._http = http

    def sync(
        self,
        debtors: Sequence[Mapping[str, Any]] | None = None,
        *,
        deudores: Sequence[Mapping[str, Any]] | None = None,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if debtors is not None:
            body["debtors"] = list(debtors)
        if deudores is not None:
            body["deudores"] = list(deudores)
        if tenant_id is not None:
            body["tenant_id"] = tenant_id
        if "debtors" not in body and "deudores" not in body:
            raise ValueError("debtors= o deudores= con al menos un deudor")
        return self._http.request("POST", "/debtors/sync", json=body)

    def list(self) -> dict[str, Any]:
        return self._http.request("GET", "/debtors")

    def get(self, debtor_ref: str) -> dict[str, Any]:
        ref = (debtor_ref or "").strip()
        if not ref:
            raise ValueError("debtor_ref es obligatorio")
        return self._http.request("GET", f"/debtors/{ref}")


class CasesResource:
    def __init__(self, http: HttpTransport) -> None:
        self._http = http

    def get(
        self,
        *,
        telefono: str = "",
        nombre: str = "",
        external_id: str = "",
    ) -> dict[str, Any]:
        params: dict[str, str] = {}
        if telefono:
            params["telefono"] = telefono
        if nombre:
            params["nombre"] = nombre
        if external_id:
            params["external_id"] = external_id
        if not params:
            raise ValueError("telefono, nombre o external_id requerido")
        return self._http.request("GET", "/cases", params=params)


class CommitmentsResource:
    def __init__(self, http: HttpTransport) -> None:
        self._http = http

    def list(self, *, limit: int = 50) -> dict[str, Any]:
        return self._http.request("GET", "/commitments", params={"limit": limit})


class PaymentsResource:
    def __init__(self, http: HttpTransport) -> None:
        self._http = http

    def register(
        self,
        *,
        amount: float,
        external_id: str | None = None,
        nombre: str | None = None,
        telefono: str | None = None,
        deudor_key: str | None = None,
        paid_at: str | None = None,
        source: str | None = "webhook",
        external_ref: str | None = None,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"amount": amount}
        if external_id is not None:
            body["external_id"] = external_id
        if nombre is not None:
            body["nombre"] = nombre
        if telefono is not None:
            body["telefono"] = telefono
        if deudor_key is not None:
            body["deudor_key"] = deudor_key
        if paid_at is not None:
            body["paid_at"] = paid_at
        if source is not None:
            body["source"] = source
        if external_ref is not None:
            body["external_ref"] = external_ref
        if tenant_id is not None:
            body["tenant_id"] = tenant_id
        return self._http.request("POST", "/payments", json=body)


class EventsResource:
    def __init__(self, http: HttpTransport) -> None:
        self._http = http

    def list(
        self,
        *,
        since: str = "",
        limit: int = 50,
        event_types: str = "",
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit}
        if since:
            params["since"] = since
        if event_types:
            params["event_types"] = event_types
        return self._http.request("GET", "/events", params=params)
