import pytest

from netdoc_sdk.client import NetDocSyncClient as NetDocClient


@pytest.mark.django_db
class TestDiscoveryRunSyncClient:
    @pytest.mark.django_db(transaction=True)
    def test_discovery_run(self, admin_sync_client, live_server):
        collector_username = 'test-collector-user'
        collector_password = 'test-password'

        # Add collector user
        admin_sync_client.user_add(
            username=collector_username, password=collector_password, role='collector'
        )
        collector_client = NetDocClient.from_credentials(
            base_url=live_server.url,
            username=collector_username,
            password=collector_password,
        )

        # Create collector (heartbeat)
        collector = collector_client.collector_heartbeat(
            name='collector@host.example.com', version='0.1.0'
        )

        # Activate collector
        admin_sync_client.collector_update(collector.id, is_active=True)

        # Create run
        discovery_run = admin_sync_client.discovery_add()
        res = admin_sync_client.discovery_list()
        assert res.count == 1
        admin_sync_client.discovery_get(id=discovery_run.id)

        # Verify jobs
        admin_sync_client.discovery_jobs(id=discovery_run.id)

        # Cancel the run
        admin_sync_client.discovery_cancel(id=discovery_run.id)
