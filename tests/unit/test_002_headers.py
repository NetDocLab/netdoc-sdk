"""
Tests for HTTP headers sent by NetDocClient.

Headers are verified by intercepting the real outbound request with respx
and reading request.headers on the captured call.
This is the only reliable approach: it tests what the server actually receives
without duplicating the internal _make_client() logic in the test suite.

httpx normalises all header names to lowercase in the request object.
"""

import httpx
import pytest
import respx

from netdoc_sdk.client import NetDocClient

BASE = 'http://fake-netdoc'
TOKEN = 'test-token-abc'

pytestmark = pytest.mark.asyncio


def _ok():
    """Minimal 200 response that satisfies PaginatedSiteList parsing."""
    return httpx.Response(200, json={'count': 0, 'next': None, 'previous': None, 'results': []})


class TestHeaders:
    @respx.mock
    async def test_token_is_sent_as_authorization_header(self):
        route = respx.get(f'{BASE}/api/v1/sites/').mock(return_value=_ok())
        async with NetDocClient(base_url=BASE, token=TOKEN) as c:
            await c.sites_list()
        assert route.calls[0].request.headers['authorization'] == f'Token {TOKEN}'

    @respx.mock
    async def test_accept_json_is_always_sent(self):
        route = respx.get(f'{BASE}/api/v1/sites/').mock(return_value=_ok())
        async with NetDocClient(base_url=BASE, token=TOKEN) as c:
            await c.sites_list()
        assert route.calls[0].request.headers['accept'] == 'application/json'

    @respx.mock
    async def test_no_authorization_header_when_token_is_omitted(self):
        route = respx.get(f'{BASE}/api/v1/sites/').mock(return_value=_ok())
        async with NetDocClient(base_url=BASE) as c:
            await c.sites_list()
        assert 'authorization' not in route.calls[0].request.headers

    @respx.mock
    async def test_tenant_id_header_is_sent_when_provided(self):
        route = respx.get(f'{BASE}/api/v1/sites/').mock(return_value=_ok())
        async with NetDocClient(base_url=BASE, token=TOKEN, tenant_id='tenant-xyz') as c:
            await c.sites_list()
        assert route.calls[0].request.headers['x-tenant-id'] == 'tenant-xyz'

    @respx.mock
    async def test_no_tenant_id_header_when_omitted(self):
        route = respx.get(f'{BASE}/api/v1/sites/').mock(return_value=_ok())
        async with NetDocClient(base_url=BASE, token=TOKEN) as c:
            await c.sites_list()
        assert 'x-tenant-id' not in route.calls[0].request.headers

    @respx.mock
    async def test_extra_headers_are_merged_into_request(self):
        route = respx.get(f'{BASE}/api/v1/sites/').mock(return_value=_ok())
        async with NetDocClient(base_url=BASE, token=TOKEN, headers={'X-Custom': 'value'}) as c:
            await c.sites_list()
        assert route.calls[0].request.headers['x-custom'] == 'value'
