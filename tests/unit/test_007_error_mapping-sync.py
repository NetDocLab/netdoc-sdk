"""
Tests for HTTP status code -> SDK exception mapping.

Each test mocks a specific HTTP response and asserts that _request raises
the correct exception class. Where the exception carries structured data
(errors dict, retry_after, status_code) that is verified too.
"""

import httpx
import pytest
import respx

from netdoc_sdk.client import NetDocSyncClient as NetDocClient
from netdoc_sdk.exceptions import (
    AuthenticationError,
    MethodNotAllowedError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    ValidationError,
)

BASE = 'http://fake-netdoc'
TOKEN = 'test-token-abc'


@pytest.fixture
def client():
    with NetDocClient(base_url=BASE, token=TOKEN, max_retries=0) as c:
        yield c


class TestErrorMappingrSyncClient:
    @respx.mock
    def test_400_raises_validation_error(self, client):
        respx.get(f'{BASE}/api/v1/sites/').mock(
            return_value=httpx.Response(400, json={'name': ['This field is required.']})
        )
        with pytest.raises(ValidationError) as exc:
            client.site_list()
        assert exc.value.errors is not None

    @respx.mock
    def test_401_raises_authentication_error(self, client):
        respx.get(f'{BASE}/api/v1/sites/').mock(
            return_value=httpx.Response(
                401, json={'detail': 'Authentication credentials were not provided.'}
            )
        )
        with pytest.raises(AuthenticationError):
            client.site_list()

    @respx.mock
    def test_403_raises_permission_denied_error(self, client):
        respx.get(f'{BASE}/api/v1/sites/').mock(
            return_value=httpx.Response(403, json={'detail': 'You do not have permission.'})
        )
        with pytest.raises(PermissionDeniedError):
            client.site_list()

    @respx.mock
    def test_404_raises_not_found_error(self, client):
        respx.get(f'{BASE}/api/v1/sites/999/').mock(
            return_value=httpx.Response(404, json={'detail': 'Not found.'})
        )
        with pytest.raises(NotFoundError):
            client.site_get('999')

    @respx.mock
    def test_404_error_message_comes_from_detail_field(self, client):
        respx.get(f'{BASE}/api/v1/sites/999/').mock(
            return_value=httpx.Response(404, json={'detail': 'Site not found.'})
        )
        with pytest.raises(NotFoundError) as exc:
            client.site_get('999')
        assert 'Site not found' in str(exc.value)

    @respx.mock
    def test_405_raises_method_not_allowed_error(self, client):
        respx.get(f'{BASE}/api/v1/sites/').mock(
            return_value=httpx.Response(405, json={'detail': 'Method not allowed.'})
        )
        with pytest.raises(MethodNotAllowedError):
            client.site_list()

    @respx.mock
    def test_429_raises_rate_limit_error_with_retry_after(self, client):
        respx.get(f'{BASE}/api/v1/sites/').mock(
            return_value=httpx.Response(
                429,
                headers={'Retry-After': '60'},
                json={'detail': 'Too many requests.'},
            )
        )
        with pytest.raises(RateLimitError) as exc:
            client.site_list()
        assert exc.value.retry_after == 60

    @respx.mock
    def test_429_retry_after_is_none_when_header_absent(self, client):
        respx.get(f'{BASE}/api/v1/sites/').mock(
            return_value=httpx.Response(429, json={'detail': 'Too many requests.'})
        )
        with pytest.raises(RateLimitError) as exc:
            client.site_list()
        assert exc.value.retry_after is None

    @respx.mock
    def test_500_raises_server_error_with_status_code(self, client):
        respx.get(f'{BASE}/api/v1/sites/').mock(
            return_value=httpx.Response(500, json={'detail': 'Internal server error.'})
        )
        with pytest.raises(ServerError) as exc:
            client.site_list()
        assert exc.value.status_code == 500

    @respx.mock
    def test_503_raises_server_error_for_non_json_body(self, client):
        # Server errors that return plain text (e.g. nginx 503) must still raise ServerError.
        respx.get(f'{BASE}/api/v1/sites/').mock(
            return_value=httpx.Response(503, content=b'Service Unavailable')
        )
        with pytest.raises(ServerError):
            client.site_list()
