"""Application configuration and credential loading."""

import os

from dotenv import load_dotenv


class ConfigurationError(Exception):
    """Raised when required application configuration is missing."""


def get_reed_api_key() -> str:
    """Return the configured Reed API key."""

    load_dotenv()

    api_key = os.getenv("REED_API_KEY")

    if not api_key or not api_key.strip():
        raise ConfigurationError(
            "REED_API_KEY is missing or empty"
        )

    return api_key.strip()