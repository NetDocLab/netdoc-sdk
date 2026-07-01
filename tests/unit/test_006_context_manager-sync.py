"""Tests for async context manager behavior.

This module verifies that the NetDocClient async context manager lifecycle
works correctly:

    - __aenter__ initializes the internal httpx client
    - __aexit__ closes and cleans up the internal client
    - Accessing .client property triggers lazy initialization
    - close() method properly cleans up resources

The context manager is the primary interface for managing HTTP connections.
"""

from netdoc_sdk.client import SyncNetDocClient as NetDocClient

BASE = 'http://fake-netdoc'
TOKEN = 'test-token-abc'


class TestContextManagerSyncClient:
    """Test async context manager lifecycle and initialization."""

    def test_aenter_creates_internal_client(self):
        """__aenter__ should initialize the internal httpx client."""
        with NetDocClient(base_url=BASE, token=TOKEN) as c:
            assert c._client is not None

    def test_aenter_returns_netdoc_client_instance(self):
        """__aenter__ should return the NetDocClient instance itself."""
        with NetDocClient(base_url=BASE, token=TOKEN) as c:
            assert isinstance(c, NetDocClient)

    def test_aexit_closes_internal_client(self):
        """__aexit__ should close the internal client and set it to None."""
        with NetDocClient(base_url=BASE, token=TOKEN) as c:
            pass
        assert c._client is None

    def test_client_property_lazily_creates_internal_client(self):
        """Accessing .client without context manager should auto-initialize."""
        # Accessing .client without a context manager must auto-initialise.
        c = NetDocClient(base_url=BASE, token=TOKEN)
        assert c._client is None
        _ = c.client
        assert c._client is not None
        c.close()

    def test_close_sets_internal_client_to_none(self):
        """close() method should clean up and set _client to None."""
        c = NetDocClient(base_url=BASE, token=TOKEN)
        _ = c.client  # force initialisation
        c.close()
        assert c._client is None
