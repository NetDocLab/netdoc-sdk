"""
Tests for NetDocClient._api_path.

Pure unit tests — no HTTP calls.
_api_path is responsible for prepending the "api/v1/" prefix to any
relative path before it is handed to httpx. These tests confirm that
the prefix is added exactly once and that leading slashes are handled.
"""

BASE = 'http://fake-netdoc'
TOKEN = 'test-token-abc'


class TestApiPath:
    def test_prefix_is_added_to_bare_path(self, client):
        assert client._api_path('sites/') == 'api/v1/sites/'

    def test_leading_slash_is_stripped_before_prefixing(self, client):
        assert client._api_path('/sites/') == 'api/v1/sites/'

    def test_prefix_is_not_doubled_when_already_present(self, client):
        # Callers that already include api/v1 must not end up with it twice.
        assert client._api_path('api/v1/sites/') == 'api/v1/sites/'

    def test_nested_path_is_preserved(self, client):
        assert client._api_path('devices/42/interfaces/') == 'api/v1/devices/42/interfaces/'

    def test_detail_path_with_id(self, client):
        assert client._api_path('sites/99/') == 'api/v1/sites/99/'
