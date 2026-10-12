"""Tests for HTTP Retry-After header parsing."""

from datetime import datetime, timezone

from app.retry_after import parse_retry_after


def test_retry_after_seconds() -> None:
    """Verify valid delta-seconds headers are parsed."""

    assert parse_retry_after("30") == 30.0
    assert parse_retry_after("0") == 0.0
    assert parse_retry_after(" 60 ") == 60.0
    assert parse_retry_after("300") == 300.0

    print("PASS: Retry-After delta-seconds parsing")


def test_invalid_retry_after() -> None:
    """Verify invalid headers are rejected."""

    assert parse_retry_after("") is None
    assert parse_retry_after("invalid") is None
    assert parse_retry_after("-5") is None
    assert parse_retry_after("1.5") is None

    print("PASS: Invalid Retry-After headers rejected")


def test_retry_after_http_date() -> None:
    """Verify HTTP-date headers produce the correct delay."""

    now = datetime(
        2026, 10, 21, 7, 27, 30,
        tzinfo=timezone.utc,
    )

    assert parse_retry_after(
        "Wed, 21 Oct 2026 07:28:00 GMT",
        now=now,
    ) == 30.0

    assert parse_retry_after(
        "Wed, 21 Oct 2026 07:27:00 GMT",
        now=now,
    ) == 0.0

    print("PASS: Retry-After HTTP-date parsing")


def test_retry_after_large_values() -> None:
    """Verify unusually large cooldown values are handled safely."""

    # A valid long cooldown must remain distinguishable
    # from a malformed header.
    assert parse_retry_after("300") == 300.0

    # A value too large for floating-point representation
    # must not crash the parser.
    enormous_value = "9" * 400

    assert parse_retry_after(enormous_value) == float("inf")

    print("PASS: Excessive Retry-After values handled safely")


def test_retry_after_malformed_dates() -> None:
    """Verify malformed HTTP-date headers are rejected."""

    assert parse_retry_after(
        "Wed, 99 Oct 2026 07:28:00 GMT"
    ) is None

    assert parse_retry_after(
        "Not a valid HTTP date"
    ) is None

    assert parse_retry_after(
        "Wed, 21 Oct 2026 07:28:00"
    ) is None

    print("PASS: Malformed Retry-After dates rejected")


def test_retry_after_timezone_handling() -> None:
    """Verify timezone-aware date calculations."""

    from datetime import timedelta

    # 08:27:30 at UTC+1 is 07:27:30 UTC.
    now = datetime(
        2026, 10, 21, 8, 27, 30,
        tzinfo=timezone(timedelta(hours=1)),
    )

    assert parse_retry_after(
        "Wed, 21 Oct 2026 07:28:00 GMT",
        now=now,
    ) == 30.0

    # A timezone-naive reference must not be accepted.
    naive_now = datetime(2026, 10, 21, 7, 27, 30)

    try:
        parse_retry_after(
            "Wed, 21 Oct 2026 07:28:00 GMT",
            now=naive_now,
        )
    except ValueError as exc:
        assert "timezone-aware" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for timezone-naive datetime"
        )

    print("PASS: Retry-After timezone handling")


if __name__ == "__main__":
    test_retry_after_seconds()
    test_invalid_retry_after()
    test_retry_after_http_date()
    test_retry_after_large_values()
    test_retry_after_malformed_dates()
    test_retry_after_timezone_handling()
