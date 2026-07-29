from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class OpenAQError(RuntimeError):
    """Raised when the OpenAQ API returns an error or unusable response."""


@dataclass(frozen=True)
class OpenAQClient:
    api_key: str
    base_url: str = "https://api.openaq.org/v3"
    timeout_seconds: int = 30

    def get_location(self, location_id: int) -> dict[str, Any]:
        return self._get_json(f"/locations/{location_id}")

    def get_latest_measurements(self, location_id: int, limit: int = 100) -> dict[str, Any]:
        return self._get_json(f"/locations/{location_id}/latest", {"limit": limit})

    def get_locations(self, params: dict[str, Any]) -> dict[str, Any]:
        return self._get_json("/locations", params)

    def _get_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        query = f"?{urlencode(params)}" if params else ""
        url = f"{self.base_url}{path}{query}"
        request = Request(url, headers={"X-API-Key": self.api_key})

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except HTTPError as exc:
            message = exc.read().decode("utf-8", errors="replace")
            raise OpenAQError(f"OpenAQ request failed with HTTP {exc.code}: {message}") from exc

        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            raise OpenAQError("OpenAQ returned a non-JSON response") from exc

        if not isinstance(payload, dict):
            raise OpenAQError("OpenAQ returned an unexpected response shape")
        return payload
