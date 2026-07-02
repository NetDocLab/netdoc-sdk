"""Tests for HTTP headers sent by NetDocClient.

This module verifies that the client constructs correct HTTP headers for all
request types. Headers are verified by intercepting outbound requests with
respx and reading request.headers on the captured call.

This is the only reliable approach: it tests what the server actually receives
without duplicating the internal _make_client() logic in the test suite.

Note:
    httpx normalizes all header names to lowercase in the request object,
    so assertions should use lowercase keys.

Test coverage:
    - Authorization header with token
    - Accept header for JSON
    - Tenant ID header when provided
    - Custom headers merged into requests
    - Headers omitted when not configured
"""

import httpx
import respx

from netdoc_sdk.client import NetDocSyncClient as NetDocClient

BASE = 'http://fake-netdoc'
TOKEN = 'test-token-abc'


def _ok():
    """Minimal 200 response that satisfies PaginatedSiteList parsing.

    Returns:
        httpx.Response: Valid paginated response for mocking.
    """
    return httpx.Response(200, json={'count': 0, 'next': None, 'previous': None, 'results': []})


class TestHeadersSyncClient:
    """Test HTTP header construction and transmission."""

    @respx.mock
    def test_token_is_sent_as_authorization_header(self):
        """Authorization header should use 'Token {token}' format."""
        route = respx.get(f'{BASE}/api/v1/sites/').mock(return_value=_ok())
        with NetDocClient(base_url=BASE, token=TOKEN) as c:
            c.sites_list()
        assert route.calls[0].request.headers['authorization'] == f'Token {TOKEN}'

    @respx.mock
    def test_accept_json_is_always_sent(self):
        """Accept header should always be set to 'application/json'."""
        route = respx.get(f'{BASE}/api/v1/sites/').mock(return_value=_ok())
        with NetDocClient(base_url=BASE, token=TOKEN) as c:
            c.sites_list()
        assert route.calls[0].request.headers['accept'] == 'application/json'

    @respx.mock
    def test_no_authorization_header_when_token_is_omitted(self):
        """Authorization header should not be sent when token is None."""
        route = respx.get(f'{BASE}/api/v1/sites/').mock(return_value=_ok())
        with NetDocClient(base_url=BASE) as c:
            c.sites_list()
        assert 'authorization' not in route.calls[0].request.headers

    @respx.mock
    def test_tenant_id_header_is_sent_when_provided(self):
        """X-Tenant-ID header should be sent when tenant_id is configured."""
        route = respx.get(f'{BASE}/api/v1/sites/').mock(return_value=_ok())
        with NetDocClient(base_url=BASE, token=TOKEN, tenant_id='tenant-xyz') as c:
            c.sites_list()
        assert route.calls[0].request.headers['x-tenant-id'] == 'tenant-xyz'

    @respx.mock
    def test_no_tenant_id_header_when_omitted(self):
        """X-Tenant-ID header should not be sent when tenant_id is None."""
        route = respx.get(f'{BASE}/api/v1/sites/').mock(return_value=_ok())
        with NetDocClient(base_url=BASE, token=TOKEN) as c:
            c.sites_list()
        assert 'x-tenant-id' not in route.calls[0].request.headers

    @respx.mock
    def test_extra_headers_are_merged_into_request(self):
        """Custom headers passed at init should be included in every request."""
        route = respx.get(f'{BASE}/api/v1/sites/').mock(return_value=_ok())
        with NetDocClient(base_url=BASE, token=TOKEN, headers={'X-Custom': 'value'}) as c:
            c.sites_list()
        assert route.calls[0].request.headers['x-custom'] == 'value'
