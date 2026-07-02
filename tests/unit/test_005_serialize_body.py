"""Tests for NetDocClient._serialize_body.

Pure unit tests for request body serialization. The _serialize_body method
merges a positional body (dict or Pydantic model) with keyword fields, dropping
None values from the keyword side. An empty result is returned as None so no
body is sent for empty requests.

Behavior:
    - Dictionaries pass through unchanged
    - Pydantic models are serialized to dictionaries
    - Keyword fields are merged with the body
    - Keyword fields override body keys
    - None keyword fields are excluded
    - Empty bodies return None
"""

from netdoc_sdk.client import NetDocClient
from netdoc_sdk.models._generated_models import SiteDetailRequest


class TestSerializeBody:
    """Test request body serialization and merging."""

    def test_plain_dict_is_passed_through(self):
        """Plain dictionary body should pass through unchanged."""
        result = NetDocClient._serialize_body({'name': 'site-a'})
        assert result == {'name': 'site-a'}

    def test_pydantic_model_is_serialised_to_dict(self):
        """Pydantic model should be converted to dictionary."""
        site = SiteDetailRequest(name='rome')
        result = NetDocClient._serialize_body(site)
        assert result['name'] == 'rome'

    def test_keyword_fields_are_merged_with_body(self):
        """Keyword fields should be merged into the body dictionary."""
        result = NetDocClient._serialize_body({'name': 'rome'}, code='RM')
        assert result == {'name': 'rome', 'code': 'RM'}

    def test_keyword_fields_override_body_keys(self):
        """Keyword fields should override keys from the body."""
        result = NetDocClient._serialize_body({'name': 'old'}, name='new')
        assert result['name'] == 'new'

    def test_none_keyword_fields_are_excluded(self):
        """None keyword fields should not appear in the result."""
        result = NetDocClient._serialize_body({'name': 'rome'}, code=None)
        assert 'code' not in result

    def test_none_body_returns_none(self):
        """None body should return None."""
        assert NetDocClient._serialize_body(None) is None

    def test_empty_dict_body_returns_none(self):
        """Empty dictionary body should return None."""
        assert NetDocClient._serialize_body({}) is None

    def test_only_none_keywords_with_no_body_returns_none(self):
        """Only None keywords with no body should return None."""
        assert NetDocClient._serialize_body(None, code=None) is None
