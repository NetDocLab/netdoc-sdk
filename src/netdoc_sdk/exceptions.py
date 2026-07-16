"""SDK-specific exceptions.

This module defines the exception hierarchy raised by the NetDoc clients when
API operations fail. All exceptions inherit from ``NetDocError`` and preserve
HTTP status codes, error details, and raw response bodies for easier debugging.

Exception Hierarchy:
    - NetDocError (base) - All SDK exceptions inherit from this
    - AuthenticationError (401) - Token or credentials are invalid or expired
    - ConnectionError - Network-level failures (not HTTP)
    - MethodNotAllowedError (405) - The endpoint does not support the requested method
    - NotFoundError (404) - The requested resource does not exist
    - PermissionDeniedError (403) - The caller lacks permission for the operation
    - RateLimitError (429) - Too many requests were sent; retry after the delay
    - ServerError (5xx) - The server encountered an error
    - ValidationError (400) - The request payload failed validation

Usage:
    from netdoc_sdk import NotFoundError, ValidationError

    try:
        snapshot = await client.snapshots_retrieve("missing")
    except NotFoundError as exc:
        print(f"Not found (status {exc.status_code}): {exc.detail}")
    except ValidationError as exc:
        print(f"Validation errors: {exc.errors}")
"""

from typing import Any


class NetDocError(Exception):
    """Base exception for all NetDoc SDK errors.

    Preserves HTTP status code, error details, and raw response body for
    detailed error inspection and handling.

    Attributes:
        message (str): Human-readable error message
        status_code (int | None): HTTP status code (None for network errors)
        detail (Any): Server-provided error detail (string or dict)
        body (Any): Full parsed response body from server
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        *,
        detail: Any = None,
        body: Any = None,
    ):
        """Initialize NetDocError.

        Args:
            message: Error message
            status_code: HTTP status code if applicable
            detail: Server error detail (keyword-only)
            body: Full response body (keyword-only)
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail
        self.body = body


class AuthenticationError(NetDocError):
    """Raised when authentication fails (HTTP 401).

    Indicates the token is missing, invalid, or expired. Check token
    configuration and regenerate if necessary.

    Attributes:
        status_code (int): Always 401
    """

    def __init__(
        self,
        message: str = 'Authentication failed',
        *,
        detail: Any = None,
        body: Any = None,
    ):
        """Initialize AuthenticationError.

        Args:
            message: Error message (default: "Authentication failed")
            detail: Server error detail (keyword-only)
            body: Full response body (keyword-only)
        """
        super().__init__(message, status_code=401, detail=detail, body=body)


class ConnectionError(NetDocError):
    """Raised when network communication fails.

    Indicates the client cannot reach the API server. This is not an HTTP
    error but a network-level failure (DNS, connection timeout, etc.).

    Causes:
        - Server is unreachable or down
        - Network connectivity issue
        - Firewall blocking connection
        - Incorrect base_url
    """

    def __init__(self, message: str = 'Failed to connect to NetDoc API'):
        """Initialize ConnectionError.

        Args:
            message: Error message (default describes connection failure)
        """
        super().__init__(message)


class MethodNotAllowedError(NetDocError):
    """Raised when HTTP method is not allowed on endpoint (HTTP 405).

    The endpoint exists but does not support the HTTP method used
    (GET, POST, PATCH, DELETE, etc.).

    Attributes:
        status_code (int): Always 405
    """

    def __init__(
        self,
        message: str = 'Method not allowed',
        *,
        detail: Any = None,
        body: Any = None,
    ):
        """Initialize MethodNotAllowedError.

        Args:
            message: Error message (default: "Method not allowed")
            detail: Server error detail (keyword-only)
            body: Full response body (keyword-only)
        """
        super().__init__(message, status_code=405, detail=detail, body=body)


class NotFoundError(NetDocError):
    """Raised when API resource does not exist (HTTP 404).

    The endpoint exists but the specific resource (identified by ID or filter)
    was not found in the database.

    Attributes:
        status_code (int): Always 404

    Example:
        try:
            snapshot = await client.snapshots_retrieve("missing-id")
        except NotFoundError:
            print("Snapshot does not exist")
    """

    def __init__(
        self,
        message: str = 'Resource not found',
        *,
        detail: Any = None,
        body: Any = None,
    ):
        """Initialize NotFoundError.

        Args:
            message: Error message (default: "Resource not found")
            detail: Server error detail (keyword-only)
            body: Full response body (keyword-only)
        """
        super().__init__(message, status_code=404, detail=detail, body=body)


class PermissionDeniedError(NetDocError):
    """Raised when user lacks permission for operation (HTTP 403).

    The authenticated user exists and the request is valid, but they do not
    have permission to perform this action. This may be due to:

    - User role (e.g., read-only user attempting write)
    - Tenant isolation (user cannot access other tenant's data)
    - Resource-level permissions

    Attributes:
        status_code (int): Always 403
    """

    def __init__(
        self,
        message: str = 'Permission denied',
        *,
        detail: Any = None,
        body: Any = None,
    ):
        """Initialize PermissionDeniedError.

        Args:
            message: Error message (default: "Permission denied")
            detail: Server error detail (keyword-only)
            body: Full response body (keyword-only)
        """
        super().__init__(message, status_code=403, detail=detail, body=body)


class RateLimitError(NetDocError):
    """Raised when client exceeds rate limits (HTTP 429).

    The API has rate-limiting enabled and this client has exceeded the limit.
    The retry_after attribute indicates how long to wait before retrying.

    Attributes:
        status_code (int): Always 429
        retry_after (int | None): Seconds to wait before retrying (if provided)
    """

    def __init__(self, retry_after: int | None = None, *, detail: Any = None, body: Any = None):
        """Initialize RateLimitError.

        Args:
            retry_after: Seconds to wait before retrying (optional)
            detail: Server error detail (keyword-only)
            body: Full response body (keyword-only)
        """
        super().__init__('Rate limit exceeded', status_code=429, detail=detail, body=body)
        self.retry_after = retry_after


class ServerError(NetDocError):
    """Raised when API returns server error (HTTP 5xx).

    Indicates a server-side error: 500, 502, 503, 504, etc. These are
    typically transient and may succeed if retried.

    Attributes:
        status_code (int): 500, 502, 503, 504, or other 5xx code
    """

    def __init__(
        self,
        message: str = 'NetDoc API server error',
        status_code: int = 500,
        *,
        detail: Any = None,
        body: Any = None,
    ):
        """Initialize ServerError.

        Args:
            message: Error message (default: "NetDoc API server error")
            status_code: Specific 5xx status code (default: 500)
            detail: Server error detail (keyword-only)
            body: Full response body (keyword-only)
        """
        super().__init__(message, status_code=status_code, detail=detail, body=body)


class ValidationError(NetDocError):
    """Raised when request data fails validation (HTTP 400).

    The request was malformed or the data fails validation constraints.
    The errors attribute contains detailed per-field validation errors.

    Attributes:
        status_code (int): Always 400
        errors (Any): Structured validation errors (dict or raw response)

    Example:
        try:
            site = await client.site_create(SiteCreate(name=""))
        except ValidationError as exc:
            print(f"Validation failed: {exc.errors}")
            # Output: {"name": ["This field may not be blank"]}
    """

    def __init__(self, message: str, errors: Any = None, *, detail: Any = None, body: Any = None):
        """Initialize ValidationError.

        Args:
            message: Error message
            errors: Structured validation errors (dict, optional)
            detail: Server error detail (keyword-only)
            body: Full response body (keyword-only)
        """
        super().__init__(message, status_code=400, detail=detail, body=body)
        self.errors = errors if errors is not None else body

    def __str__(self) -> str:
        """Include errors in string representation for better error messages."""
        if self.errors:
            return f'{self.message}: {self.errors}'
        return self.message
