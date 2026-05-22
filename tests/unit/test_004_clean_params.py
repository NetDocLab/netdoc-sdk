"""
Tests for NetDocClient._clean_params.

Pure unit tests — no HTTP calls.
_clean_params strips None values from query-parameter dicts so they are
never serialised into the URL. An empty result is returned as None so
httpx does not append a bare "?" to the URL.
"""

from netdoc_sdk.client import NetDocClient


class TestCleanParams:
    def test_none_values_are_removed(self):
        result = NetDocClient._clean_params({'a': 1, 'b': None, 'c': 'x'})
        assert result == {'a': 1, 'c': 'x'}

    def test_empty_dict_returns_none(self):
        assert NetDocClient._clean_params({}) is None

    def test_dict_of_all_nones_returns_none(self):
        assert NetDocClient._clean_params({'a': None, 'b': None}) is None

    def test_none_input_returns_none(self):
        assert NetDocClient._clean_params(None) is None

    def test_zero_is_kept(self):
        # Numeric zero is a valid filter value and must not be dropped.
        result = NetDocClient._clean_params({'page': 0})
        assert result == {'page': 0}

    def test_false_is_kept(self):
        result = NetDocClient._clean_params({'active': False})
        assert result == {'active': False}

    def test_empty_string_is_kept(self):
        result = NetDocClient._clean_params({'q': ''})
        assert result == {'q': ''}
