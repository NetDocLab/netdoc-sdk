"""Shared fixtures and test utilities for NetDocClient unit tests.

This module provides pytest fixtures and constants used across all unit tests.
Unit tests focus on isolated behavior and API contracts using mocked HTTP responses.

Fixtures:
    - client: Synchronous NetDocClient for testing static attributes
    - client: Async NetDocClient for HTTP mocking tests

Constants:
    - BASE: Fake NetDoc server URL for all unit tests
    - TOKEN: Test authentication token
    - PAGINATED_EMPTY: Empty paginated API response template
"""

import pytest

from netdoc_sdk.client import NetDocClient, NetDocSyncClient

BASE = 'http://fake-netdoc'
TOKEN = 'test-token-abc'

PAGINATED_EMPTY = {'count': 0, 'next': None, 'previous': None, 'results': []}


@pytest.fixture
def sync_client():
    """Synchronous NetDocClient instance.

    Used for testing pure attributes, static methods, and initialization logic
    that don't require HTTP calls. No mocking or fixtures needed.

    Returns:
        NetDocClient: Client configured with test BASE URL and TOKEN.
    """
    return NetDocSyncClient(base_url=BASE, token=TOKEN)


@pytest.fixture
async def client():
    """Async NetDocClient instance opened as async context manager.

    Used for tests that make mocked HTTP calls via respx. The client is
    automatically opened and closed by the fixture, providing a properly
    initialized async session.

    Yields:
        NetDocClient: Async-enabled client ready for HTTP mocking.

    Example:
        @respx.mock
        async def test_something(client):
            route = respx.get(...).mock(return_value=...)
            await client.method_call()
            assert route.called
    """
    async with NetDocClient(base_url=BASE, token=TOKEN) as c:
        yield c
