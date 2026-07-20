from __future__ import annotations

from typing import Any, Mapping

import httpx

from kobra_partner._http import DEFAULT_TIMEOUT, HttpTransport
from kobra_partner.resources import (
    CasesResource,
    CommitmentsResource,
    DebtorsResource,
    EventsResource,
    PaymentsResource,
)


class Client:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        transport: httpx.BaseTransport | None = None,
        extra_headers: Mapping[str, str] | None = None,
    ) -> None:
        self._http = HttpTransport(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            transport=transport,
            extra_headers=extra_headers,
        )
        self.debtors = DebtorsResource(self._http)
        self.cases = CasesResource(self._http)
        self.commitments = CommitmentsResource(self._http)
        self.payments = PaymentsResource(self._http)
        self.events = EventsResource(self._http)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def me(self) -> dict[str, Any]:
        return self._http.request("GET", "/me")

    def summary(self) -> dict[str, Any]:
        return self._http.request("GET", "/summary")

    def capabilities(self) -> dict[str, Any]:
        return self._http.request("GET", "/sdk-map")
