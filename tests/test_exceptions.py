from app.exceptions import (
    AuthenticationError,
    JobSearchHTTPError,
    NetworkError,
    RateLimitError,
    ResponseFormatError,
    ServerError,
)


def test_exception_hierarchy() -> None:
    """Verify all HTTP exceptions inherit from the base exception."""

    exception_types = (
        AuthenticationError,
        RateLimitError,
        ServerError,
        NetworkError,
        ResponseFormatError,
    )

    for exception_type in exception_types:
        assert issubclass(exception_type, JobSearchHTTPError)

    print("PASS: All custom exceptions inherit from JobSearchHTTPError")


def test_exception_message() -> None:
    """Verify exceptions preserve useful error messages."""

    error = ServerError("Reed API returned HTTP 503")

    assert str(error) == "Reed API returned HTTP 503"
    assert isinstance(error, JobSearchHTTPError)

    print("PASS: Custom exceptions preserve error messages")


if __name__ == "__main__":
    test_exception_hierarchy()
    test_exception_message()
