import pytest


@pytest.mark.django_db
class TestCanonicalDevice:
    @pytest.mark.django_db(transaction=True)
    async def test_canonical_device(self, admin_client):
        site = await admin_client.sites_add(name='test-site')
        canonical_device = await admin_client.canonical_devices_add(
            label='test-canonical-device',
            identifiers={'hostname': 'r1'},
            site=site.id,
        )
        res = await admin_client.canonical_devices_list()
        assert res.count == 1
        await admin_client.canonical_devices_get(id=canonical_device.id)
        await admin_client.canonical_devices_update(
            id=canonical_device.id, label='test-new-canmonical-device'
        )
        await admin_client.canonical_devices_delete(id=canonical_device.id)
        # TODO
        # await admin_client.canonical_devices_history(id=canonical_device.id)
