import pytest


@pytest.mark.django_db
class TestCanonicalDevice:
    @pytest.mark.django_db(transaction=True)
    async def test_canonical_device(self, admin_client):
        canonical_device = await admin_client.canonicaldevice_add(
            label='test-canonical-device',
            identifiers={'hostname': 'r1'},
        )
        res = await admin_client.canonicaldevice_list()
        assert res.count == 1
        await admin_client.canonicaldevice_get(id=canonical_device.id)
        await admin_client.canonicaldevice_update(
            id=canonical_device.id, name='test-new-canmonical-device'
        )
        await admin_client.canonicaldevice_delete(id=canonical_device.id)
        # TODO
        # await admin_client.canonicaldevice_history(id=canonical_device.id)
