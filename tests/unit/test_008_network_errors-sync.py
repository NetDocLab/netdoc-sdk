"""
Tests for network-level error handling.

ConnectError and timeout exceptions raised by httpx must be caught
and re-raised as the SDK's own ConnectionError so callers never
need to import httpx to handle transport failures.
"""

import httpx
import pytest
import respx

from netdoc_sdk.client import NetDocSyncClient as NetDocClient
from netdoc_sdk.exceptions import ConnectionError

BASE = 'http://fake-netdoc'
TOKEN = 'test-token-abc'


@pytest.fixture
def client():
    with NetDocClient(base_url=BASE, token=TOKEN) as c:
        yield c


class TestNetworkErrorsrSyncClient:
    @respx.mock
    def test_connect_error_raises_sdk_connection_error(self, client):
        respx.get(f'{BASE}/api/v1/sites/').mock(
            side_effect=httpx.ConnectError('Connection refused')
        )
        with pytest.raises(ConnectionError):
            client.site_list()

    @respx.mock
    def test_read_timeout_raises_sdk_connection_error(self, client):
        respx.get(f'{BASE}/api/v1/sites/').mock(side_effect=httpx.ReadTimeout('Read timed out'))
        with pytest.raises(ConnectionError):
            client.site_list()

    @respx.mock
    def test_connect_timeout_raises_sdk_connection_error(self, client):
        respx.get(f'{BASE}/api/v1/sites/').mock(
            side_effect=httpx.ConnectTimeout('Connect timed out')
        )
        with pytest.raises(ConnectionError):
            client.site_list()
