from app.retry_policy import RetryPolicy


def test_default_configuration() -> None:
    """Verify the default retry settings."""

    policy = RetryPolicy()

    assert policy.max_attempts == 4
    assert policy.initial_delay == 1.0
    assert policy.backoff_multiplier == 2.0
    assert policy.max_delay == 8.0
    assert policy.jitter_max == 0.25

    print("PASS: Default retry policy configuration")


def test_invalid_max_attempts() -> None:
    """Verify zero attempts are rejected."""

    try:
        RetryPolicy(max_attempts=0)
    except ValueError as exc:
        assert "max_attempts" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for zero attempts"
        )

    print("PASS: Invalid maximum attempts rejected")


def test_exponential_backoff() -> None:
    """Verify exponential delays and the maximum cap."""

    policy = RetryPolicy()

    delays = [
        policy.backoff_delay(n)
        for n in range(1, 6)
    ]

    assert delays == [1.0, 2.0, 4.0, 8.0, 8.0]

    print("PASS: Exponential backoff and delay cap")


def test_invalid_retry_number() -> None:
    """Verify retry numbers must start at one."""

    policy = RetryPolicy()

    try:
        policy.backoff_delay(0)
    except ValueError as exc:
        assert "retry_number" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for invalid retry number"
        )

    print("PASS: Invalid retry number rejected")


def test_fixed_jitter() -> None:
    """Verify deterministic jitter calculations."""

    policy = RetryPolicy()

    delays = [
        policy.delay_with_jitter(n, jitter=0.2)
        for n in range(1, 6)
    ]

    assert delays == [1.2, 2.2, 4.2, 8.0, 8.0]

    print("PASS: Fixed jitter and maximum delay cap")


def test_invalid_jitter() -> None:
    """Verify jitter cannot exceed its configured range."""

    policy = RetryPolicy()

    try:
        policy.delay_with_jitter(1, jitter=0.5)
    except ValueError as exc:
        assert "jitter" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for invalid jitter"
        )

    print("PASS: Invalid jitter rejected")


def test_random_jitter_bounds() -> None:
    """Verify generated jitter remains within its limits."""

    policy = RetryPolicy()

    delays = [
        policy.delay_with_jitter(1)
        for _ in range(100)
    ]

    assert all(1.0 <= delay <= 1.25 for delay in delays)

    print("PASS: Random jitter remains within bounds")


if __name__ == "__main__":
    test_default_configuration()
    test_invalid_max_attempts()
    test_exponential_backoff()
    test_invalid_retry_number()
    test_fixed_jitter()
    test_invalid_jitter()
    test_random_jitter_bounds()
