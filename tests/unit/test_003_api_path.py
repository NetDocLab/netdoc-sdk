"""Tests for NetDocClient._api_path.

Pure unit tests for API path construction. The _api_path method is responsible
for prepending the "api/v1/" prefix to any relative path before it is handed
to httpx. These tests confirm that:

    - The prefix is added exactly once
    - Leading slashes are handled correctly
    - Nested and detail paths are preserved
    - Double-prefixing is avoided when /api/v1 already present
"""

BASE = 'http://fake-netdoc'
TOKEN = 'test-token-abc'


class TestApiPath:
    """Test API path construction and prefix handling."""

    def test_prefix_is_added_to_bare_path(self, client):
        """Bare path should get 'api/v1/' prefix."""
        assert client._api_path('sites/') == 'api/v1/sites/'

    def test_leading_slash_is_stripped_before_prefixing(self, client):
        """Leading slash should be removed before adding prefix."""
        assert client._api_path('/sites/') == 'api/v1/sites/'

    def test_prefix_is_not_doubled_when_already_present(self, client):
        """When /api/v1 already included, it should not be added again."""
        # Callers that already include api/v1 must not end up with it twice.
        assert client._api_path('api/v1/sites/') == 'api/v1/sites/'

    def test_nested_path_is_preserved(self, client):
        """Nested paths with multiple segments should be handled correctly."""
        assert client._api_path('devices/42/interfaces/') == 'api/v1/devices/42/interfaces/'

    def test_detail_path_with_id(self, client):
        """Detail paths with IDs should be prefixed normally."""
        assert client._api_path('sites/99/') == 'api/v1/sites/99/'
