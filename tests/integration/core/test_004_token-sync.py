import pytest

from netdoc_sdk.client import NetDocSyncClient as NetDocClient


@pytest.mark.django_db
class TestTokenSyncClient:
    @pytest.mark.django_db(transaction=True)
    def test_user(self, admin_sync_client, live_server):
        username = 'conftest-admin'
        password = '986629a7ca89202a3ef2ae1dd9d5fb37'
        client = NetDocClient.from_credentials(
            base_url=live_server.url,
            username=username,
            password=password,
        )
        client.tokens_add(username=username, password=password)
