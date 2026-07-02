import pytest

from netdoc_sdk.client import NetDocSyncClient as NetDocClient


@pytest.mark.django_db
class TestDiscoveryRunSyncClient:
    @pytest.mark.django_db(transaction=True)
    def test_discoveries_run(self, admin_sync_client, live_server):
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

        # Activate collector
        admin_sync_client.collectors_update(collector.id, is_active=True)

        # Create run
        discoveries_run = admin_sync_client.discoveries_add()
        res = admin_sync_client.discoveries_list()
        assert res.count == 1
        admin_sync_client.discoveries_get(id=discoveries_run.id)

        # Verify jobs
        admin_sync_client.discoveries_jobs_list(id=discoveries_run.id)

        # Cancel the run
        admin_sync_client.discoveries_cancel(id=discoveries_run.id)
