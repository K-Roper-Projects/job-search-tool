import time
from collections.abc import Callable
from json import JSONDecodeError
from typing import Any

import httpx

from app.exceptions import (
    AuthenticationError,
    JobSearchHTTPError,
    NetworkError,
    RateLimitError,
    ResponseFormatError,
    ServerError,
)

from app.retry_policy import RetryPolicy


def is_retryable_network_error(exc: httpx.RequestError) -> bool:
    """Identify network failures that are safe to retry."""

    if isinstance(
        exc,
        (
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
            httpx.WriteTimeout,
            httpx.PoolTimeout,
            httpx.ReadError,
            httpx.WriteError,
            httpx.CloseError,
        ),
    ):
        return True

    return False


class HTTPClient:
    """Shared synchronous HTTP client for external job APIs."""


    def __init__(
        self,
        *,
        transport: httpx.BaseTransport | None = None,
        retry_policy: RetryPolicy | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._retry_policy = (
            retry_policy
            if retry_policy is not None
            else RetryPolicy()
        )

        self._sleep = sleep

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

        retryable_statuses = {500, 502, 503, 504}

        for attempt in range(1, self._retry_policy.max_attempts + 1):
            try:
                response = self._client.get(
                    url,
                    params=params,
                    headers=headers,
                    auth=auth,
                )

                response.raise_for_status()
                break

            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code

                if (
                    status_code in retryable_statuses
                    and attempt < self._retry_policy.max_attempts
                ):
                    delay = self._retry_policy.delay_with_jitter(attempt)
                    self._sleep(delay)
                    continue

                if status_code in (401, 403):
                    raise AuthenticationError(
                        f"API authentication failed: HTTP {status_code}"
                    ) from exc

                if status_code == 429:
                    raise RateLimitError(
                        "API rate limit exceeded: HTTP 429"
                    ) from exc

                if 500 <= status_code <= 599:
                    raise ServerError(
                        f"API server failure: HTTP {status_code}"
                    ) from exc

                raise JobSearchHTTPError(
                    f"API request failed: HTTP {status_code}"
                ) from exc

            except httpx.RequestError as exc:
                if (
                    is_retryable_network_error(exc)
                    and attempt < self._retry_policy.max_attempts
                ):
                    delay = self._retry_policy.delay_with_jitter(attempt)
                    self._sleep(delay)
                    continue

                raise NetworkError(
                    "API network request failed"
                ) from exc


        try:
            return response.json()

        except (JSONDecodeError, UnicodeDecodeError) as exc:
            raise ResponseFormatError(
                "API returned invalid JSON"
            ) from exc


    def close(self) -> None:
        """Release network connections and associated resources."""
        self._client.close()

    def __enter__(self) -> "HTTPClient":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()
