"""Utilities for interpreting HTTP Retry-After headers."""

import math
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime


def parse_retry_after(
    value: str,
    *,
    now: datetime | None = None,
) -> float | None:
    """Return the requested delay in seconds, or None if invalid."""

    value = value.strip()

    if not value:
        return None

    # Retry-After may contain a non-negative integer number of seconds.
    if value.isascii() and value.isdecimal():
        try:
            delay = float(value)
        except (ValueError, OverflowError):
            return math.inf

        if not math.isfinite(delay):
            return math.inf

        return delay

    # Otherwise, attempt to interpret it as an HTTP date.
    try:
        retry_date = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError, OverflowError):
        return None

    if retry_date is None or retry_date.tzinfo is None:
        return None

    if now is None:
        now = datetime.now(timezone.utc)

    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")

    delay = (retry_date - now).total_seconds()

    if not math.isfinite(delay):
        return None

    return max(0.0, delay)
