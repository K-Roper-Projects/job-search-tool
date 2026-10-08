import httpx

from app.exceptions import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ResponseFormatError,
    ServerError,
    JobSearchHTTPError,
)
from app.http_client import HTTPClient
from app.retry_policy import RetryPolicy


def mock_handler(request: httpx.Request) -> httpx.Response:
    """Simulate a successful API response."""

    assert request.method == "GET"
    assert request.url.scheme == "https"
    assert request.url.params["keywords"] == "cloud engineer"

    return httpx.Response(
        status_code=200,
        json={
            "results": [
                {
                    "id": "123",
                    "title": "Cloud Engineer",
                    "location": "Cambridge",
                }
            ]
        },
    )


def test_successful_get_json() -> None:
    """Verify HTTPS GET requests and JSON decoding."""

    with HTTPClient(
        transport=httpx.MockTransport(mock_handler),
    ) as client:
        data = client.get_json(
            "https://example.com/api/jobs",
            params={"keywords": "cloud engineer"},
        )

    assert data["results"][0]["id"] == "123"
    assert data["results"][0]["title"] == "Cloud Engineer"

    print("PASS: HTTPS GET request and JSON decoding")


def test_unauthorized_response() -> None:
    """Verify that an HTTP 401 response raises an error."""

    def unauthorized_handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=401,
            json={"error": "Unauthorized"},
        )

    with HTTPClient(
        transport=httpx.MockTransport(unauthorized_handler),
    ) as client:
        try:
            client.get_json("https://example.com/api/jobs")
        except AuthenticationError as exc:
            assert "HTTP 401" in str(exc)
            assert isinstance(exc.__cause__, httpx.HTTPStatusError)
            assert exc.__cause__.response.status_code == 401
        else:
            raise AssertionError(
                "Expected AuthenticationError for HTTP 401"
            )

    print("PASS: HTTP 401 (Unauthorized) raises AuthenticationError")


def test_forbidden_response() -> None:
    """Verify that HTTP 403 raises AuthenticationError."""

    def forbidden_handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=403,
            json={"error": "Forbidden"},
        )

    with HTTPClient(
        transport=httpx.MockTransport(forbidden_handler),
    ) as client:
        try:
            client.get_json("https://example.com/api/jobs")
        except AuthenticationError as exc:
            assert "HTTP 403" in str(exc)
            assert isinstance(exc.__cause__, httpx.HTTPStatusError)
            assert exc.__cause__.response.status_code == 403
        else:
            raise AssertionError(
                "Expected AuthenticationError for HTTP 403"
            )

    print("PASS: HTTP 403 (Forbidden) raises AuthenticationError")


def test_not_found_response() -> None:
    """Verify that HTTP 404 raises the general HTTP error."""

    def not_found_handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=404,
            json={"error": "Not Found"},
        )

    with HTTPClient(
        transport=httpx.MockTransport(not_found_handler),
    ) as client:
        try:
            client.get_json("https://example.com/api/jobs/123")
        except JobSearchHTTPError as exc:
            assert type(exc) is JobSearchHTTPError
            assert "HTTP 404" in str(exc)
            assert isinstance(exc.__cause__, httpx.HTTPStatusError)
            assert exc.__cause__.response.status_code == 404
        else:
            raise AssertionError(
                "Expected JobSearchHTTPError for HTTP 404"
            )

    print("PASS: HTTP 404 (Not Found) raises JobSearchHTTPError")


def test_network_timeout() -> None:
    """Verify that a timeout raises NetworkError."""

    def timeout_handler(
        request: httpx.Request,
    ) -> httpx.Response:
        raise httpx.ReadTimeout(
            "Simulated API read timeout",
            request=request,
        )

    with HTTPClient(
        transport=httpx.MockTransport(timeout_handler),
        retry_policy=RetryPolicy(max_attempts=1),
    ) as client:
        try:
            client.get_json("https://example.com/api/jobs")
        except NetworkError as exc:
            assert isinstance(exc.__cause__, httpx.ReadTimeout)
        else:
            raise AssertionError(
                "Expected NetworkError for a read timeout"
            )

    print("PASS: Network timeout raises NetworkError")


def test_internal_server_error() -> None:
    """Verify that an HTTP 500 response raises an error."""

    def server_error_handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=500,
            json={"error": "Internal Server Error"},
        )

    with HTTPClient(
        transport=httpx.MockTransport(server_error_handler),
        retry_policy=RetryPolicy(max_attempts=1),
    ) as client:
        try:
            client.get_json("https://example.com/api/jobs")
        except ServerError as exc:
            assert "HTTP 500" in str(exc)
            assert isinstance(exc.__cause__, httpx.HTTPStatusError)
            assert exc.__cause__.response.status_code == 500
        else:
            raise AssertionError(
                "Expected ServerError for HTTP 500"
            )

    print("PASS: HTTP 500 raises ServerError")


def test_retry_recovers_after_server_errors() -> None:
    """Verify two HTTP 503 failures recover on the third attempt."""

    request_count = 0
    sleep_delays: list[float] = []

    def recovery_handler(
        request: httpx.Request,
    ) -> httpx.Response:
        nonlocal request_count
        request_count += 1

        if request_count <= 2:
            return httpx.Response(
                status_code=503,
                json={"error": "Service Unavailable"},
            )

        return httpx.Response(
            status_code=200,
            json={"jobs": [{"id": 123, "title": "Cloud Engineer"}]},
        )

    with HTTPClient(
        transport=httpx.MockTransport(recovery_handler),
        retry_policy=RetryPolicy(
            max_attempts=4,
            jitter_max=0.0,
        ),
        sleep=sleep_delays.append,
    ) as client:
        result = client.get_json(
            "https://example.com/api/jobs"
        )

    assert request_count == 3
    assert sleep_delays == [1.0, 2.0]
    assert result == {
        "jobs": [{"id": 123, "title": "Cloud Engineer"}]
    }

    print("PASS: HTTP 503 retries recover on third attempt")


def test_retry_exhaustion() -> None:
    """Verify retries stop after the maximum attempts."""

    request_count = 0
    sleep_delays: list[float] = []

    def unavailable_handler(
        request: httpx.Request,
    ) -> httpx.Response:
        nonlocal request_count
        request_count += 1

        return httpx.Response(
            status_code=503,
            json={"error": "Service Unavailable"},
        )

    with HTTPClient(
        transport=httpx.MockTransport(unavailable_handler),
        retry_policy=RetryPolicy(
            max_attempts=4,
            jitter_max=0.0,
        ),
        sleep=sleep_delays.append,
    ) as client:
        try:
            client.get_json("https://example.com/api/jobs")
        except ServerError as exc:
            assert "HTTP 503" in str(exc)
            assert isinstance(
                exc.__cause__,
                httpx.HTTPStatusError,
            )
            assert exc.__cause__.response.status_code == 503
        else:
            raise AssertionError(
                "Expected ServerError after retry exhaustion"
            )

    assert request_count == 4
    assert sleep_delays == [1.0, 2.0, 4.0]

    print("PASS: Retry exhaustion stops after four attempts")


def test_network_timeout_recovery() -> None:
    """Verify the client recovers after two read timeouts."""

    request_count = 0
    sleep_delays: list[float] = []

    def recovery_handler(
        request: httpx.Request,
    ) -> httpx.Response:
        nonlocal request_count
        request_count += 1

        if request_count <= 2:
            raise httpx.ReadTimeout(
                "Simulated temporary read timeout",
                request=request,
            )

        return httpx.Response(
            status_code=200,
            json={
                "jobs": [
                    {"id": 456, "title": "Platform Engineer"}
                ]
            },
        )

    with HTTPClient(
        transport=httpx.MockTransport(recovery_handler),
        retry_policy=RetryPolicy(
            max_attempts=4,
            jitter_max=0.0,
        ),
        sleep=sleep_delays.append,
    ) as client:
        result = client.get_json(
            "https://example.com/api/jobs"
        )

    assert request_count == 3
    assert sleep_delays == [1.0, 2.0]
    assert result == {
        "jobs": [
            {"id": 456, "title": "Platform Engineer"}
        ]
    }

    print("PASS: Network timeout recovers on third attempt")


def test_network_retry_exhaustion() -> None:
    """Verify network retries stop after maximum attempts."""

    request_count = 0
    sleep_delays: list[float] = []

    def timeout_handler(
        request: httpx.Request,
    ) -> httpx.Response:
        nonlocal request_count
        request_count += 1

        raise httpx.ReadTimeout(
            "Simulated persistent read timeout",
            request=request,
        )

    with HTTPClient(
        transport=httpx.MockTransport(timeout_handler),
        retry_policy=RetryPolicy(
            max_attempts=4,
            jitter_max=0.0,
        ),
        sleep=sleep_delays.append,
    ) as client:
        try:
            client.get_json("https://example.com/api/jobs")
        except NetworkError as exc:
            assert isinstance(
                exc.__cause__,
                httpx.ReadTimeout,
            )
        else:
            raise AssertionError(
                "Expected NetworkError after retry exhaustion"
            )

    assert request_count == 4
    assert sleep_delays == [1.0, 2.0, 4.0]

    print("PASS: Network retries stop after four timeouts")


def test_connect_error_does_not_retry() -> None:
    """Verify ambiguous connection failures stop immediately."""

    request_count = 0
    sleep_delays: list[float] = []

    def connection_error_handler(
        request: httpx.Request,
    ) -> httpx.Response:
        nonlocal request_count
        request_count += 1

        raise httpx.ConnectError(
            "Simulated TLS certificate verification failure",
            request=request,
        )

    with HTTPClient(
        transport=httpx.MockTransport(connection_error_handler),
        retry_policy=RetryPolicy(
            max_attempts=4,
            jitter_max=0.0,
        ),
        sleep=sleep_delays.append,
    ) as client:
        try:
            client.get_json("https://example.com/api/jobs")
        except NetworkError as exc:
            assert isinstance(
                exc.__cause__,
                httpx.ConnectError,
            )
        else:
            raise AssertionError(
                "Expected NetworkError for connection failure"
            )

    assert request_count == 1
    assert sleep_delays == []

    print("PASS: ConnectError does not trigger retries")


def test_authentication_failure_does_not_retry() -> None:
    """Verify authentication failures stop after one request."""

    request_count = 0
    sleep_delays: list[float] = []

    def unauthorized_handler(
        request: httpx.Request,
    ) -> httpx.Response:
        nonlocal request_count
        request_count += 1

        return httpx.Response(
            status_code=401,
            json={"error": "Unauthorized"},
        )

    with HTTPClient(
        transport=httpx.MockTransport(unauthorized_handler),
        retry_policy=RetryPolicy(
            max_attempts=4,
            jitter_max=0.0,
        ),
        sleep=sleep_delays.append,
    ) as client:
        try:
            client.get_json("https://example.com/api/jobs")
        except AuthenticationError as exc:
            assert "HTTP 401" in str(exc)
        else:
            raise AssertionError(
                "Expected AuthenticationError for HTTP 401"
            )

    assert request_count == 1
    assert sleep_delays == []

    print("PASS: Authentication failure does not retry")


def test_rate_limit_response() -> None:
    """Verify that HTTP 429 raises RateLimitError."""

    def rate_limit_handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=429,
            headers={"Retry-After": "30"},
            json={"error": "Too Many Requests"},
        )

    with HTTPClient(
        transport=httpx.MockTransport(rate_limit_handler),
    ) as client:
        try:
            client.get_json("https://example.com/api/jobs")
        except RateLimitError as exc:
            assert "HTTP 429" in str(exc)
            assert isinstance(exc.__cause__, httpx.HTTPStatusError)
            assert exc.__cause__.response.status_code == 429
            assert exc.__cause__.response.headers["Retry-After"] == "30"
        else:
            raise AssertionError(
                "Expected RateLimitError for HTTP 429"
            )

    print("PASS: HTTP 429 raises RateLimitError")


def test_invalid_json_response() -> None:
    """Verify that malformed JSON raises a decoding error."""

    def invalid_json_handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            text="This is not valid JSON!",
        )

    with HTTPClient(
        transport=httpx.MockTransport(invalid_json_handler),
    ) as client:
        try:
            client.get_json("https://example.com/api/jobs")
        except ResponseFormatError:
            pass
        else:
            raise AssertionError(
                "Expected ResponseFormatError for invalid JSON"
            )

    print("PASS: Invalid JSON raises ResponseFormatError")


def test_reject_insecure_http() -> None:
    """Verify that HTTP URLs are rejected before any request."""

    def unexpected_request_handler(
        request: httpx.Request,
    ) -> httpx.Response:
        raise AssertionError(
            "Network transport must not be called for HTTP URLs"
        )

    with HTTPClient(
        transport=httpx.MockTransport(unexpected_request_handler),
    ) as client:
        try:
            client.get_json("http://example.com/api/jobs")
        except ValueError as exc:
            assert str(exc) == "Only HTTPS URLs are permitted"
        else:
            raise AssertionError(
                "Expected ValueError for an insecure HTTP URL"
            )

    print("PASS: Insecure HTTP URL rejected")


def test_reject_missing_hostname() -> None:
    """Verify HTTPS URLs without a hostname are rejected."""

    def unexpected_request_handler(
        request: httpx.Request,
    ) -> httpx.Response:
        raise AssertionError(
            "Network transport must not be called for invalid URLs"
        )

    with HTTPClient(
        transport=httpx.MockTransport(unexpected_request_handler),
    ) as client:
        try:
            client.get_json("https://")
        except ValueError as exc:
            assert str(exc) in (
                "Invalid URL",
                "Only HTTPS URLs are permitted",
            )
        else:
            raise AssertionError(
                "Expected ValueError for URL without hostname"
            )

    print("PASS: HTTPS URL without hostname rejected")


if __name__ == "__main__":
    test_successful_get_json()
    test_unauthorized_response()
    test_forbidden_response()
    test_not_found_response()
    test_network_timeout()
    test_internal_server_error()
    test_retry_recovers_after_server_errors()
    test_retry_exhaustion()
    test_network_timeout_recovery()
    test_network_retry_exhaustion()
    test_connect_error_does_not_retry()
    test_authentication_failure_does_not_retry()
    test_invalid_json_response()
    test_reject_insecure_http()
    test_reject_missing_hostname()
    test_rate_limit_response()
