import httpx

from app.http_client import is_retryable_network_error


def test_retryable_timeouts() -> None:
    """Verify transient timeout errors are retryable."""

    request = httpx.Request(
        "GET",
        "https://example.com/api/jobs",
    )

    exceptions = [
        httpx.ConnectTimeout("Connection timed out", request=request),
        httpx.ReadTimeout("Read timed out", request=request),
        httpx.WriteTimeout("Write timed out", request=request),
        httpx.PoolTimeout("Connection pool timed out", request=request),
    ]

    assert all(
        is_retryable_network_error(exc)
        for exc in exceptions
    )

    print("PASS: Transient network timeouts are retryable")


def test_retryable_transport_errors() -> None:
    """Verify selected transport failures are retryable."""

    request = httpx.Request(
        "GET",
        "https://example.com/api/jobs",
    )

    exceptions = [
        httpx.ReadError("Read failed", request=request),
        httpx.WriteError("Write failed", request=request),
        httpx.CloseError("Connection closed", request=request),
    ]

    assert all(
        is_retryable_network_error(exc)
        for exc in exceptions
    )

    print("PASS: Selected transport errors are retryable")


def test_connect_error_not_retryable() -> None:
    """Verify ambiguous connection errors are not retried."""

    request = httpx.Request(
        "GET",
        "https://example.com/api/jobs",
    )

    exc = httpx.ConnectError(
        "SSL certificate verify failed",
        request=request,
    )

    assert not is_retryable_network_error(exc)

    print("PASS: Ambiguous connection errors are not retried")


if __name__ == "__main__":
    test_retryable_timeouts()
    test_retryable_transport_errors()
    test_connect_error_not_retryable()
