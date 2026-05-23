"""
Tests for NetDocClient._serialize_body.

Pure unit tests — no HTTP calls.
_serialize_body merges a positional body (dict or Pydantic model) with
keyword fields, dropping None values from the keyword side. An empty
result is returned as None so no body is sent for empty requests.
"""

import uuid
from netdoc_sdk.client import NetDocClient
from netdoc_sdk.models.inventory import SiteCreate


class TestSerializeBody:
    def test_plain_dict_is_passed_through(self):
        result = NetDocClient._serialize_body({'name': 'site-a'})
        assert result == {'name': 'site-a'}

    def test_pydantic_model_is_serialised_to_dict(self):
        site = SiteCreate(name='rome')
        result = NetDocClient._serialize_body(site)
        assert result['name'] == 'rome'

    def test_keyword_fields_are_merged_with_body(self):
        result = NetDocClient._serialize_body({'name': 'rome'}, code='RM')
        assert result == {'name': 'rome', 'code': 'RM'}

    def test_keyword_fields_override_body_keys(self):
        result = NetDocClient._serialize_body({'name': 'old'}, name='new')
        assert result['name'] == 'new'

    def test_none_keyword_fields_are_excluded(self):
        result = NetDocClient._serialize_body({'name': 'rome'}, code=None)
        assert 'code' not in result

    def test_none_body_returns_none(self):
        assert NetDocClient._serialize_body(None) is None

    def test_empty_dict_body_returns_none(self):
        assert NetDocClient._serialize_body({}) is None

    def test_only_none_keywords_with_no_body_returns_none(self):
        assert NetDocClient._serialize_body(None, code=None) is None
