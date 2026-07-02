"""Tests for NetDocClient._normalize_base_url.

This module contains pure unit tests for URL normalization logic. No HTTP calls
are made, and no fixtures are required beyond the base configuration constants.

Each test constructs a client with a specific input URL and asserts that
base_url is stored in the expected normalized form.

Normalization rules:
    - Trailing slashes are removed
    - '/api/v1' suffix is stripped if already present
    - Empty strings fall back to localhost
    - Plain URLs are left unchanged
"""

from netdoc_sdk.client import NetDocSyncClient as NetDocClient

BASE = 'http://fake-netdoc'
TOKEN = 'test-token-abc'


class TestNormalizeBaseUrlSyncClient:
    """Test URL normalization logic in NetDocClient initialization."""

    def test_plain_url_is_unchanged(self):
        """Plain URL without trailing slash or /api/v1 should be stored as-is."""
        c = NetDocClient(base_url=BASE, token=TOKEN)
        assert c.base_url == BASE

    def test_trailing_slash_is_stripped(self):
        """URL with trailing slash should have it removed."""
        c = NetDocClient(base_url=f'{BASE}/', token=TOKEN)
        assert c.base_url == BASE

    def test_api_v1_suffix_is_stripped(self):
        """URL ending in /api/v1 should have it removed to avoid doubling."""
        # Passing a URL that already includes /api/v1 should not double the prefix.
        c = NetDocClient(base_url=f'{BASE}/api/v1', token=TOKEN)
        assert c.base_url == BASE

    def test_api_v1_with_trailing_slash_is_stripped(self):
        """URL ending in /api/v1/ should have both /api/v1 and trailing slash removed."""
        c = NetDocClient(base_url=f'{BASE}/api/v1/', token=TOKEN)
        assert c.base_url == BASE

    def test_empty_string_falls_back_to_localhost(self):
        """Empty string base_url should fall back to a localhost-based URL."""
        c = NetDocClient(base_url='', token=TOKEN)
        assert 'localhost' in c.base_url
