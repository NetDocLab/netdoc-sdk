"""Tests for NetDocClient._clean_params.

Pure unit tests for query parameter cleaning. The _clean_params method strips
None values from query-parameter dictionaries so they are never serialized into
the URL. An empty result is returned as None so httpx does not append a bare
"?" to the URL.

Behavior:
    - None values are removed from dictionaries
    - Falsy values (0, False, '') are preserved (valid filter values)
    - Empty dictionaries return None
    - None input returns None
"""

from netdoc_sdk.client import SyncNetDocClient as NetDocClient


class TestCleanParamsSyncClient:
    """Test query parameter cleaning logic."""

    def test_none_values_are_removed(self):
        """None values should be stripped from the parameter dict."""
        result = NetDocClient._clean_params({'a': 1, 'b': None, 'c': 'x'})
        assert result == {'a': 1, 'c': 'x'}

    def test_empty_dict_returns_none(self):
        """Empty dictionary should return None, not empty dict."""
        assert NetDocClient._clean_params({}) is None

    def test_dict_of_all_nones_returns_none(self):
        """Dictionary with only None values should return None."""
        assert NetDocClient._clean_params({'a': None, 'b': None}) is None

    def test_none_input_returns_none(self):
        """None input should return None."""
        assert NetDocClient._clean_params(None) is None

    def test_zero_is_kept(self):
        """Numeric zero is a valid filter value and must not be dropped."""
        # Numeric zero is a valid filter value and must not be dropped.
        result = NetDocClient._clean_params({'page': 0})
        assert result == {'page': 0}

    def test_false_is_kept(self):
        """Boolean False is a valid filter value and must not be dropped."""
        result = NetDocClient._clean_params({'active': False})
        assert result == {'active': False}

    def test_empty_string_is_kept(self):
        """Empty string is a valid filter value and must not be dropped."""
        result = NetDocClient._clean_params({'q': ''})
        assert result == {'q': ''}
