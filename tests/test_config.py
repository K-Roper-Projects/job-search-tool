"""Tests for application configuration loading."""

import os
from unittest.mock import patch

from app.config import ConfigurationError, get_reed_api_key


def test_valid_reed_api_key() -> None:
    """Verify a configured API key is returned."""

    with patch.dict(os.environ, {"REED_API_KEY": "dummy-test-key"}):
        api_key = get_reed_api_key()

    assert api_key == "dummy-test-key"

    print("PASS: Valid Reed API key loaded")


def test_missing_reed_api_key() -> None:
    """Verify a missing API key raises ConfigurationError."""

    with patch("app.config.load_dotenv"):
        with patch.dict(os.environ, {}, clear=True):
            try:
                get_reed_api_key()
            except ConfigurationError as exc:
                assert "REED_API_KEY" in str(exc)
            else:
                raise AssertionError(
                    "Expected ConfigurationError for missing API key"
                )

    print("PASS: Missing Reed API key rejected")


def test_empty_reed_api_key() -> None:
    """Verify empty and whitespace-only keys are rejected."""

    for invalid_key in ("", "   "):
        with patch.dict(os.environ, {"REED_API_KEY": invalid_key}):
            try:
                get_reed_api_key()
            except ConfigurationError as exc:
                assert "REED_API_KEY" in str(exc)
            else:
                raise AssertionError(
                    "Expected ConfigurationError for empty API key"
                )

    print("PASS: Empty Reed API key rejected")


if __name__ == "__main__":
    test_valid_reed_api_key()
    test_missing_reed_api_key()
    test_empty_reed_api_key()