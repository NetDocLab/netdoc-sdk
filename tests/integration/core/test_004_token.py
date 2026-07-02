import pytest

from netdoc_sdk.client import NetDocClient


@pytest.mark.django_db
class TestToken:
    @pytest.mark.django_db(transaction=True)
    async def test_user(self, admin_client, live_server):
        username = 'conftest-admin'
        password = '986629a7ca89202a3ef2ae1dd9d5fb37'
        client = await NetDocClient.from_credentials(
            base_url=live_server.url,
            username=username,
            password=password,
        )
        await client.tokens_add(username=username, password=password)
