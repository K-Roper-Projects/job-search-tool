from json import JSONDecodeError

import httpx

from app.http_client import HTTPClient


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
        except httpx.HTTPStatusError as exc:
            assert exc.response.status_code == 401
        else:
            raise AssertionError(
                "Expected HTTPStatusError for HTTP 401"
            )

    print("PASS: HTTP 401 raises HTTPStatusError")


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
    ) as client:
        try:
            client.get_json("https://example.com/api/jobs")
        except httpx.HTTPStatusError as exc:
            assert exc.response.status_code == 500
        else:
            raise AssertionError(
                "Expected HTTPStatusError for HTTP 500"
            )

    print("PASS: HTTP 500 raises HTTPStatusError")


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
        except JSONDecodeError:
            pass
        else:
            raise AssertionError(
                "Expected JSONDecodeError for invalid JSON"
            )

    print("PASS: Invalid JSON raises JSONDecodeError")


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
    test_internal_server_error()
    test_invalid_json_response()
    test_reject_insecure_http()
    test_reject_missing_hostname()
