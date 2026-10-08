class JobSearchHTTPError(Exception):
    """Base exception for HTTP failures in the Job Search Tool."""


class AuthenticationError(JobSearchHTTPError):
    """API authentication or authorisation failed."""


class RateLimitError(JobSearchHTTPError):
    """An API rate limit has been reached."""


class ServerError(JobSearchHTTPError):
    """An external API returned a server-side error."""


class NetworkError(JobSearchHTTPError):
    """A network connection or transport failure occurred."""


class ResponseFormatError(JobSearchHTTPError):
    """An API returned an invalid or unexpected response format."""
