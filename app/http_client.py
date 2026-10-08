from typing import Any

import httpx


class HTTPClient:
    """Shared synchronous HTTP client for external job APIs."""

    def __init__(
        self,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        timeout = httpx.Timeout(
            connect=5.0,
            read=15.0,
            write=5.0,
            pool=5.0,
        )

        self._client = httpx.Client(
            timeout=timeout,
            follow_redirects=False,
            trust_env=False,
            transport=transport,
        )

    def get_json(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        auth: httpx.Auth | None = None,
    ) -> Any:
        """Perform an HTTPS GET request and return decoded JSON."""

        try:
            parsed_url = httpx.URL(url)
        except (httpx.InvalidURL, TypeError) as exc:
            raise ValueError("Invalid URL") from exc

        if parsed_url.scheme != "https" or not parsed_url.host:
            raise ValueError("Only HTTPS URLs are permitted")

        response = self._client.get(
            url,
            params=params,
            headers=headers,
            auth=auth,
        )

        response.raise_for_status()

        return response.json()

    def close(self) -> None:
        """Release network connections and associated resources."""
        self._client.close()

    def __enter__(self) -> "HTTPClient":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()
