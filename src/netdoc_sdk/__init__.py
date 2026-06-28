"""NetDoc SDK - Async Python client for the NetDoc API.

This package provides a type-safe, async/await interface to the NetDoc
network documentation API (v1). It handles authentication, HTTP communication,
response parsing, and error handling.

Quick Start:
    from netdoc_sdk import NetDocClient

    async with NetDocClient(base_url="...", token="...") as client:
        snapshots = await client.snapshots_list()

Available Exports:

    Client:
        - NetDocClient: Main async HTTP client

    Exceptions:
        - NetDocError: Base exception
        - AuthenticationError: Token/credentials invalid (401)
        - ConnectionError: Network communication failure
        - NotFoundError: Resource does not exist (404)
        - PermissionDeniedError: User lacks permission (403)
        - ValidationError: Request validation failed (400)
        - RateLimitError: Rate limit exceeded (429)
        - ServerError: Server error (5xx)
        - MethodNotAllowedError: HTTP method not allowed (405)

    Models:
        All Pydantic models for API responses are automatically exported:
        - Snapshot-related: SnapshotDetail, PaginatedSnapshotList, ...
        - Inventory-related: SiteDetail, CanonicalDeviceDetail, ...
        - Discovery-related: CredentialDetail, DiscoveryJobDetail, ...
        - Core-related: UserDetail, TenantDetail, TokenRequest, ...

Usage:
    Import the client:
        from netdoc_sdk import NetDocClient

    Import exception types:
        from netdoc_sdk import NotFoundError, ValidationError

    Import models:
        from netdoc_sdk.models.snapshots import SnapshotDetail
        or simply:
        from netdoc_sdk import SnapshotDetail  # Auto-exported

See https://github.com/netdoclab/netdoc-sdk for documentation.
"""

from netdoc_sdk.client import NetDocClient
from netdoc_sdk.exceptions import (  # noqa: F401
    AuthenticationError,
    ConnectionError,
    MethodNotAllowedError,
    NetDocError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from netdoc_sdk.models import core as _core  # noqa: F401
from netdoc_sdk.models import discovery as _discovery  # noqa: F401
from netdoc_sdk.models import inventory as _inventory  # noqa: F401
from netdoc_sdk.models import snapshots as _snapshots  # noqa: F401

models = []
for model in ['_core', '_snapshots', '_discovery', '_inventory']:
    models += [name for name in dir(model) if not name.startswith('_')]
    del model


__all__ = [
    'AuthenticationError',
    'ConnectionError',
    'MethodNotAllowedError',
    'NetDocClient',
    'NetDocError',
    'NotFoundError',
    'PermissionDeniedError',
    'RateLimitError',
    'ServerError',
    'ValidationError',
    *models,
]

