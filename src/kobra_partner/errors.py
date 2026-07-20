from __future__ import annotations

from typing import Any


class KobraError(Exception):
    pass


class APIError(KobraError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        body: Any = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.body = body
        self.headers = headers or {}

    def __str__(self) -> str:
        if self.status_code is not None:
            return f"{self.status_code}: {self.message}"
        return self.message


class AuthenticationError(APIError):
    pass


class NotFoundError(APIError):
    pass


class RateLimitError(APIError):
    pass
