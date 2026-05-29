"""SDK-specific exceptions."""

from typing import Any


class NetDocError(Exception):
    """Base exception for NetDoc SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        *,
        detail: Any = None,
        body: Any = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail
        self.body = body


class AuthenticationError(NetDocError):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = 'Authentication failed',
        *,
        detail: Any = None,
        body: Any = None,
    ):
        super().__init__(message, status_code=401, detail=detail, body=body)


class ConnectionError(NetDocError):
    """Raised when the client cannot reach the API."""

    def __init__(self, message: str = 'Failed to connect to NetDoc API'):
        super().__init__(message)


class MethodNotAllowedError(NetDocError):
    """Raised when an endpoint rejects the HTTP method."""

    def __init__(
        self,
        message: str = 'Method not allowed',
        *,
        detail: Any = None,
        body: Any = None,
    ):
        super().__init__(message, status_code=405, detail=detail, body=body)


class NotFoundError(NetDocError):
    """Raised when an API resource does not exist."""

    def __init__(
        self,
        message: str = 'Resource not found',
        *,
        detail: Any = None,
        body: Any = None,
    ):
        super().__init__(message, status_code=404, detail=detail, body=body)


class PermissionDeniedError(NetDocError):
    """Raised when the authenticated user is not allowed to perform an action."""

    def __init__(
        self,
        message: str = 'Permission denied',
        *,
        detail: Any = None,
        body: Any = None,
    ):
        super().__init__(message, status_code=403, detail=detail, body=body)


class RateLimitError(NetDocError):
    """Raised when rate limited by the API."""

    def __init__(self, retry_after: int | None = None, *, detail: Any = None, body: Any = None):
        super().__init__('Rate limit exceeded', status_code=429, detail=detail, body=body)
        self.retry_after = retry_after


class ServerError(NetDocError):
    """Raised when the API returns a 5xx response."""

    def __init__(
        self,
        message: str = 'NetDoc API server error',
        status_code: int = 500,
        *,
        detail: Any = None,
        body: Any = None,
    ):
        super().__init__(message, status_code=status_code, detail=detail, body=body)


class ValidationError(NetDocError):
    """Raised when request data is invalid."""

    def __init__(self, message: str, errors: Any = None, *, detail: Any = None, body: Any = None):
        super().__init__(message, status_code=400, detail=detail, body=body)
        self.errors = errors if errors is not None else body

    def __str__(self) -> str:
        if self.errors:
            return f'{self.message}: {self.errors}'
        return self.message
