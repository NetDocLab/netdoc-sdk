"""Top-level package for the NetDoc SDK.

This package exposes a type-safe client for NetDoc's `/api/v1` API. It handles
authentication, HTTP communication, response parsing, and error handling for both
asynchronous and synchronous usage.

Quick Start:
    from netdoc_sdk import NetDocClient

    async with NetDocClient(base_url="https://netdoc.example.com", token="...") as client:
        snapshots = await client.snapshots_list()

Available Exports:

    Client:
        - NetDocClient: Async client for asyncio applications
        - NetDocSyncClient: Synchronous client for blocking environments

    Exceptions:
        - NetDocError: Base exception for SDK failures
        - AuthenticationError: Token or credentials are invalid (401)
        - ConnectionError: The server could not be reached
        - NotFoundError: The requested resource does not exist (404)
        - PermissionDeniedError: Access is not allowed (403)
        - ValidationError: The request payload is invalid (400)
        - RateLimitError: The API rate limit was exceeded (429)
        - ServerError: The API returned a server-side error (5xx)
        - MethodNotAllowedError: The endpoint does not support the requested method (405)

    Models:
        Pydantic models for request and response payloads are exported automatically.

See https://github.com/netdoclab/netdoc-sdk for documentation.
"""

from netdoc_sdk.client import NetDocClient
from netdoc_sdk.exceptions import (
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
from netdoc_sdk.models import _generated_models  # noqa: F401

models = [name for name in dir('_generated_models') if not name.startswith('_')]


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
