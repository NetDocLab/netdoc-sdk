import pytest
from netdoc_sdk.client import NetDocClient


@pytest.mark.django_db
class TestCollector:
    @pytest.mark.django_db(transaction=True)
    async def test_collector(self, admin_client, live_server):
        collector_username='test-collector-user'
        collector_password='test-password'

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
        collector = await collector_client.collector_heartbeat(name="collector@host.example.com", version="0.1.0")

        # Test admin functions
        res = await admin_client.collector_list()
        assert res.count == 1
        await admin_client.collector_get(id=collector.id)
        await admin_client.collector_update(id=collector.id, is_active=False)
        await admin_client.collector_delete(id=collector.id)
