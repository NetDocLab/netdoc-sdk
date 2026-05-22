"""
Tests for NetDocClient._normalize_base_url.

These are pure unit tests — no HTTP calls, no fixtures needed.
Each test constructs a client with a specific input URL and
asserts that base_url is stored in the expected normalized form.
"""

from netdoc_sdk.client import NetDocClient

BASE = 'http://fake-netdoc'
TOKEN = 'test-token-abc'


class TestNormalizeBaseUrl:
    def test_plain_url_is_unchanged(self):
        c = NetDocClient(base_url=BASE, token=TOKEN)
        assert c.base_url == BASE

    def test_trailing_slash_is_stripped(self):
        c = NetDocClient(base_url=f'{BASE}/', token=TOKEN)
        assert c.base_url == BASE

    def test_api_v1_suffix_is_stripped(self):
        # Passing a URL that already includes /api/v1 should not double the prefix.
        c = NetDocClient(base_url=f'{BASE}/api/v1', token=TOKEN)
        assert c.base_url == BASE

    def test_api_v1_with_trailing_slash_is_stripped(self):
        c = NetDocClient(base_url=f'{BASE}/api/v1/', token=TOKEN)
        assert c.base_url == BASE

    def test_empty_string_falls_back_to_localhost(self):
        c = NetDocClient(base_url='', token=TOKEN)
        assert 'localhost' in c.base_url
