"""
Tests for NetDocClient.from_credentials.

from_credentials is a factory method that calls POST /api/v1/tokens/,
extracts the token from the response and returns a fully authenticated
client. These tests verify the request body, the returned client state,
and error propagation on invalid credentials.
"""

import json
import httpx
import pytest
import respx
from netdoc_sdk.client import NetDocClient
from netdoc_sdk.exceptions import AuthenticationError

BASE = 'http://fake-netdoc'

pytestmark = pytest.mark.asyncio


class TestFromCredentials:
    @respx.mock
    async def test_returns_authenticated_netdoc_client(self):
        respx.post(f'{BASE}/api/v1/tokens/').mock(
            return_value=httpx.Response(200, json={'token': 'generated-token-xyz'})
        )
        client = await NetDocClient.from_credentials(
            base_url=BASE, username='admin', password='secret'
        )
        assert isinstance(client, NetDocClient)
        assert client.token == 'generated-token-xyz'
        await client.close()

    @respx.mock
    async def test_request_body_contains_username_and_password(self):
        route = respx.post(f'{BASE}/api/v1/tokens/').mock(
            return_value=httpx.Response(200, json={'token': 'tok'})
        )
        await NetDocClient.from_credentials(base_url=BASE, username='admin', password='secret')
        payload = json.loads(route.calls[0].request.read())
        assert payload['username'] == 'admin'
        assert payload['password'] == 'secret'

    @respx.mock
    async def test_invalid_credentials_raise_authentication_error(self):
        respx.post(f'{BASE}/api/v1/tokens/').mock(
            return_value=httpx.Response(401, json={'detail': 'Invalid credentials.'})
        )
        with pytest.raises(AuthenticationError):
            await NetDocClient.from_credentials(base_url=BASE, username='wrong', password='wrong')

    @respx.mock
    async def test_base_url_is_normalised_on_returned_client(self):
        respx.post(f'{BASE}/api/v1/tokens/').mock(
            return_value=httpx.Response(200, json={'token': 'tok'})
        )
        # Pass URL with trailing slash — the returned client should strip it.
        client = await NetDocClient.from_credentials(
            base_url=f'{BASE}/', username='admin', password='secret'
        )
        assert client.base_url == BASE
        await client.close()
