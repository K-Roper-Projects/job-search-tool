from dataclasses import dataclass

import random


@dataclass(frozen=True)
class RetryPolicy:
    """Configuration for bounded HTTP request retries."""

    max_attempts: int = 4
    initial_delay: float = 1.0
    backoff_multiplier: float = 2.0
    max_delay: float = 8.0
    jitter_max: float = 0.25

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError(
                "max_attempts must be at least 1"
            )

        if self.initial_delay < 0:
            raise ValueError(
                "initial_delay cannot be negative"
            )

        if self.backoff_multiplier < 1:
            raise ValueError(
                "backoff_multiplier must be at least 1"
            )

        if self.max_delay < 0:
            raise ValueError(
                "max_delay cannot be negative"
            )

        if self.jitter_max < 0:
            raise ValueError(
                "jitter_max cannot be negative"
            )


    def backoff_delay(self, retry_number: int) -> float:
        """Calculate the capped delay before a retry."""

        if retry_number < 1:
            raise ValueError(
                "retry_number must be at least 1"
            )

        delay = self.initial_delay * (
            self.backoff_multiplier ** (retry_number - 1)
        )

        return min(delay, self.max_delay)


    def delay_with_jitter(
        self,
        retry_number: int,
        *,
        jitter: float | None = None,
    ) -> float:
        """Calculate capped exponential backoff with jitter."""

        base_delay = self.backoff_delay(retry_number)

        if jitter is None:
            jitter = random.uniform(0.0, self.jitter_max)

        if not 0.0 <= jitter <= self.jitter_max:
            raise ValueError(
                "jitter must be between 0 and jitter_max"
            )

        return min(base_delay + jitter, self.max_delay)
