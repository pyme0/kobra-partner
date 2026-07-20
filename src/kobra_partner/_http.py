from __future__ import annotations

from typing import Any, Mapping

import httpx

from kobra_partner._version import __version__
from kobra_partner.errors import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)

DEFAULT_TIMEOUT = 30.0
API_PREFIX = "/api/partner/v1"
HEADER_API_KEY = "X-Kobra-Partner-Key"


class HttpTransport:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout: float = DEFAULT_TIMEOUT,
        transport: httpx.BaseTransport | None = None,
        extra_headers: Mapping[str, str] | None = None,
    ) -> None:
        if not api_key or not str(api_key).strip():
            raise AuthenticationError("api_key es obligatorio", status_code=None)
        base = (base_url or "").strip().rstrip("/")
        if not base:
            raise APIError("base_url es obligatorio")

        headers = {
            HEADER_API_KEY: str(api_key).strip(),
            "Accept": "application/json",
            "User-Agent": f"kobra-partner-python/{__version__}",
        }
        if extra_headers:
            headers.update(dict(extra_headers))

        self._client = httpx.Client(
            base_url=base,
            headers=headers,
            timeout=timeout,
            transport=transport,
        )

    def close(self) -> None:
        try:
            self._client.close()
        except Exception:
            pass

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        url = path if path.startswith("/") else f"/{path}"
        if not url.startswith(API_PREFIX):
            url = f"{API_PREFIX}{url if url.startswith('/') else '/' + url}"

        try:
            resp = self._client.request(method, url, json=json, params=params)
        except httpx.HTTPError as exc:
            raise APIError(f"error de red: {exc}") from exc

        return self._parse(resp)

    def _parse(self, resp: httpx.Response) -> Any:
        try:
            body = resp.json() if resp.content else None
        except ValueError:
            body = resp.text

        if resp.is_success:
            return body

        message = _message_from_body(body) or resp.reason_phrase or "error de API"
        headers = {k.lower(): v for k, v in resp.headers.items()}
        if resp.status_code in (401, 403):
            raise AuthenticationError(
                message, status_code=resp.status_code, body=body, headers=headers
            )
        if resp.status_code == 404:
            raise NotFoundError(
                message, status_code=resp.status_code, body=body, headers=headers
            )
        if resp.status_code == 429:
            raise RateLimitError(
                message, status_code=resp.status_code, body=body, headers=headers
            )
        raise APIError(
            message, status_code=resp.status_code, body=body, headers=headers
        )


def _message_from_body(body: Any) -> str | None:
    if body is None:
        return None
    if isinstance(body, str) and body.strip():
        return body.strip()
    if not isinstance(body, dict):
        return None
    detail = body.get("detail")
    if isinstance(detail, str) and detail.strip():
        return detail.strip()
    if isinstance(detail, list) and detail:
        first = detail[0]
        if isinstance(first, dict):
            return str(first.get("msg") or first)
        return str(first)
    if body.get("message"):
        return str(body["message"])
    if body.get("error"):
        return str(body["error"])
    return None
