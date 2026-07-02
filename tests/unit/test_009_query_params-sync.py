"""
Tests for query parameter serialisation.

Verifies that filter kwargs are forwarded as URL query params and that
None values are silently dropped (never appear in the URL).
"""

import httpx
import pytest
import respx

from netdoc_sdk.client import NetDocSyncClient as NetDocClient

BASE = 'http://fake-netdoc'
TOKEN = 'test-token-abc'

_EMPTY_PAGE = {'count': 0, 'next': None, 'previous': None, 'results': []}


@pytest.fixture
def client():
    with NetDocClient(base_url=BASE, token=TOKEN) as c:
        yield c


class TestQueryParamsrSyncClient:
    @respx.mock
    def test_filter_kwargs_appear_in_url(self, client):
        route = respx.get(f'{BASE}/api/v1/sites/').mock(
            return_value=httpx.Response(200, json=_EMPTY_PAGE)
        )
        client.sites_list(name='milan')
        assert 'name=milan' in str(route.calls[0].request.url)

    @respx.mock
    def test_multiple_filters_all_appear_in_url(self, client):
        route = respx.get(f'{BASE}/api/v1/sites/').mock(
            return_value=httpx.Response(200, json=_EMPTY_PAGE)
        )
        client.sites_list(name='milan', page=2)
        url = str(route.calls[0].request.url)
        assert 'name=milan' in url
        assert 'page=2' in url

    @respx.mock
    def test_none_filter_is_not_sent(self, client):
        route = respx.get(f'{BASE}/api/v1/sites/').mock(
            return_value=httpx.Response(200, json=_EMPTY_PAGE)
        )
        client.sites_list(name=None)
        assert 'name' not in str(route.calls[0].request.url)

    @respx.mock
    def test_no_query_string_when_no_filters(self, client):
        route = respx.get(f'{BASE}/api/v1/sites/').mock(
            return_value=httpx.Response(200, json=_EMPTY_PAGE)
        )
        client.sites_list()
        assert '?' not in str(route.calls[0].request.url)
