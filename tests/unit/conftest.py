"""Shared fixtures for NetDocClient unit tests."""

import pytest

from netdoc_sdk.client import NetDocClient

BASE = 'http://fake-netdoc'
TOKEN = 'test-token-abc'

PAGINATED_EMPTY = {'count': 0, 'next': None, 'previous': None, 'results': []}


@pytest.fixture
def client():
    """Synchronous client instance — used for testing pure attributes and static methods."""
    return NetDocClient(base_url=BASE, token=TOKEN)


@pytest.fixture
async def async_client():
    """Async client opened as context manager — used for tests that make HTTP calls."""
    async with NetDocClient(base_url=BASE, token=TOKEN) as c:
        yield c
