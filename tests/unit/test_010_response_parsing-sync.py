"""
Tests for HTTP response -> Pydantic model parsing.

Verifies that _request deserialises the JSON body into the declared
response_model and that edge cases (204, empty body) return None.
"""

import uuid

import httpx
import pytest
import respx

from netdoc_sdk.exceptions import ValidationError
from netdoc_sdk.models._generated_models import PaginatedSiteListList, SiteDetail

BASE = 'http://fake-netdoc'
TOKEN = 'test-token-abc'


class TestResponseParsingSyncClient:
    @respx.mock
    async def test_list_endpoint_returns_paginated_model(self, sync_client):
        respx.get(f'{BASE}/api/v1/sites/').mock(
            return_value=httpx.Response(
                200,
                json={
                    'count': 1,
                    'next': None,
                    'previous': None,
                    'results': [
                        {
                            'id': str(uuid.uuid4()),
                            'name': 'milan',
                            'site_type': 'branch',
                            'is_default': True,
                            'address': '',
                            'city': '',
                            'region': '',
                            'country': '',
                            'created_at': '2026-05-23 06:37:34.246550Z',
                            'updated_at': '2026-05-23 06:37:34.246550Z',
                        }
                    ],
                },
            )
        )
        result = sync_client.sites_list()
        assert isinstance(result, PaginatedSiteListList)
        assert result.count == 1
        assert result.results[0].name == 'milan'

    @respx.mock
    async def test_retrieve_endpoint_returns_model_instance(self, sync_client):
        site_id = str(uuid.uuid4())
        respx.get(f'{BASE}/api/v1/sites/1/').mock(
            return_value=httpx.Response(
                200,
                json={
                    'id': site_id,
                    'name': 'milan',
                    'site_type': 'branch',
                    'address': '',
                    'city': '',
                    'region': '',
                    'country': '',
                    'created_at': '2026-05-23 06:37:34.246550Z',
                    'updated_at': '2026-05-23 06:37:34.246550Z',
                },
            )
        )
        result = sync_client.sites_get('1')
        assert isinstance(result, SiteDetail)
        assert result.id == site_id
        assert result.name == 'milan'

    @respx.mock
    async def test_204_no_content_returns_none(self, sync_client):
        respx.delete(f'{BASE}/api/v1/sites/1/').mock(return_value=httpx.Response(204))
        result = sync_client.sites_delete('1')
        assert result is None

    @respx.mock
    async def test_empty_body_raises(self, sync_client):
        # A 200 response with no body is unexpected and must raise ServerError.
        respx.get(f'{BASE}/api/v1/sites/').mock(return_value=httpx.Response(200, content=b''))
        with pytest.raises(ValidationError):
            sync_client.sites_list()
