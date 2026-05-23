"""
Tests for async context manager behaviour.

Verifies that __aenter__ initialises the internal httpx client and
__aexit__ closes it, and that accessing .client outside a context
manager triggers lazy initialisation.
"""

import pytest

from netdoc_sdk.client import NetDocClient

BASE = 'http://fake-netdoc'
TOKEN = 'test-token-abc'

pytestmark = pytest.mark.asyncio


class TestContextManager:
    async def test_aenter_creates_internal_client(self):
        async with NetDocClient(base_url=BASE, token=TOKEN) as c:
            assert c._client is not None

    async def test_aenter_returns_netdoc_client_instance(self):
        async with NetDocClient(base_url=BASE, token=TOKEN) as c:
            assert isinstance(c, NetDocClient)

    async def test_aexit_closes_internal_client(self):
        async with NetDocClient(base_url=BASE, token=TOKEN) as c:
            pass
        assert c._client is None

    async def test_client_property_lazily_creates_internal_client(self):
        # Accessing .client without a context manager must auto-initialise.
        c = NetDocClient(base_url=BASE, token=TOKEN)
        assert c._client is None
        _ = c.client
        assert c._client is not None
        await c.close()

    async def test_close_sets_internal_client_to_none(self):
        c = NetDocClient(base_url=BASE, token=TOKEN)
        _ = c.client  # force initialisation
        await c.close()
        assert c._client is None
