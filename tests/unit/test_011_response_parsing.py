"""
Tests for HTTP response -> Pydantic model parsing.

Verifies that _request deserialises the JSON body into the declared
response_model and that edge cases (204, empty body) return None.
"""

from __future__ import annotations

import httpx
import pytest
import respx

from netdoc_sdk.models import PaginatedSiteList, Site

BASE = 'http://fake-netdoc'
TOKEN = 'test-token-abc'

pytestmark = pytest.mark.asyncio


class TestResponseParsing:
    @respx.mock
    async def test_list_endpoint_returns_paginated_model(self, client):
        respx.get(f'{BASE}/api/v1/sites/').mock(
            return_value=httpx.Response(
                200,
                json={
                    'count': 1,
                    'next': None,
                    'previous': None,
                    'results': [{'id': '1', 'name': 'milan'}],
                },
            )
        )
        result = await client.sites_list()
        assert isinstance(result, PaginatedSiteList)
        assert result.count == 1
        assert result.results[0].name == 'milan'

    @respx.mock
    async def test_retrieve_endpoint_returns_model_instance(self, client):
        respx.get(f'{BASE}/api/v1/sites/1/').mock(
            return_value=httpx.Response(200, json={'id': '1', 'name': 'milan'})
        )
        result = await client.sites_retrieve('1')
        assert isinstance(result, Site)
        assert result.id == '1'
        assert result.name == 'milan'

    @respx.mock
    async def test_204_no_content_returns_none(self, client):
        respx.delete(f'{BASE}/api/v1/sites/1/').mock(return_value=httpx.Response(204))
        result = await client.sites_destroy('1')
        assert result is None

    @respx.mock
    async def test_empty_body_returns_none(self, client):
        # Some endpoints may return 200 with no body; must not raise.
        respx.get(f'{BASE}/api/v1/sites/').mock(return_value=httpx.Response(200, content=b''))
        result = await client.sites_list()
        assert result is None
