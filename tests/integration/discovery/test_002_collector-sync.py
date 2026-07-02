import pytest

from netdoc_sdk.client import NetDocSyncClient as NetDocClient


@pytest.mark.django_db
class TestCanonicalDeviceSyncClient:
    @pytest.mark.django_db(transaction=True)
    def test_collector(self, admin_sync_client, live_server):
        collector_username = 'test-collector-user'
        collector_password = 'test-password'

        # Add collector user
        admin_sync_client.users_add(
            username=collector_username, password=collector_password, role='collector'
        )
        collector_client = NetDocClient.from_credentials(
            base_url=live_server.url,
            username=collector_username,
            password=collector_password,
        )

        # Create collector (heartbeat)
        collector = collector_client.collectors_heartbeat(
            name='collector@host.example.com', version='0.1.0'
        )

        # Test functions
        res = admin_sync_client.collectors_list()
        assert res.count == 1
        admin_sync_client.collectors_get(id=collector.id)
        admin_sync_client.collectors_update(id=collector.id, is_active=False)
        admin_sync_client.collectors_delete(id=collector.id)
