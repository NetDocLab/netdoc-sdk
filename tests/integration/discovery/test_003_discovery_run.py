import pytest

from netdoc_sdk.client import NetDocClient


@pytest.mark.django_db
class TestDiscoveryRun:
    @pytest.mark.django_db(transaction=True)
    async def test_discoveries_run(self, admin_client, live_server):
        collector_username = 'test-collector-user'
        collector_password = 'test-password'

        # Add collector user
        await admin_client.users_add(
            username=collector_username, password=collector_password, role='collector'
        )
        collector_client = await NetDocClient.from_credentials(
            base_url=live_server.url,
            username=collector_username,
            password=collector_password,
        )

        # Create collector (heartbeat)
        collector = await collector_client.collectors_heartbeat(
            name='collector@host.example.com', version='0.1.0'
        )

        # Activate collector
        await admin_client.collectors_update(collector.id, is_active=True)

        # Create run
        discoveries_run = await admin_client.discoveries_add()
        res = await admin_client.discoveries_list()
        assert res.count == 1
        await admin_client.discoveries_get(id=discoveries_run.id)

        # Verify jobs
        await admin_client.discoveries_jobs_list(id=discoveries_run.id)

        # Cancel the run
        await admin_client.discoveries_cancel(id=discoveries_run.id)
