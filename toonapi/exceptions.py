"""Exceptions for the Quby ToonAPI."""


class ToonError(Exception):
    """Generic ToonAPI exception."""


class ToonConnectionError(ToonError):
    """ToonAPI connection exception."""


class ToonConnectionTimeoutError(ToonConnectionError):
    """ToonAPI connection timeout exception."""


class ToonRateLimitError(ToonConnectionError):
    """ToonAPI Rate Limit exception."""
