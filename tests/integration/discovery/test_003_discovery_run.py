import pytest

from netdoc_sdk.client import NetDocClient


@pytest.mark.django_db
class TestDiscoveryRun:
    @pytest.mark.django_db(transaction=True)
    async def test_discovery_run(self, admin_client, live_server):
        collector_username = 'test-collector-user'
        collector_password = 'test-password'

        # Add collector user
        await admin_client.user_add(
            username=collector_username, password=collector_password, role='collector'
        )
        collector_client = await NetDocClient.from_credentials(
            base_url=live_server.url,
            username=collector_username,
            password=collector_password,
        )

        # Create collector (heartbeat)
        await collector_client.collector_heartbeat(
            name='collector@host.example.com', version='0.1.0'
        )

        # Test functions
        discovery_run = await admin_client.discovery_add()
        res = await admin_client.discovery_list()
        assert res.count == 1
        await admin_client.discovery_get(id=discovery_run.id)
        # TODO: await admin_client.discovery_jobs(id=discovery_run.id)
        await admin_client.discovery_cancel(id=discovery_run.id)
