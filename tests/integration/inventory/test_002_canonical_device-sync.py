import pytest


@pytest.mark.django_db
class TestCanonicalDeviceSyncClient:
    @pytest.mark.django_db(transaction=True)
    def test_canonical_device(self, admin_sync_client):
        canonical_device = admin_sync_client.canonicaldevice_add(
            label='test-canonical-device',
            identifiers={'hostname': 'r1'},
        )
        res = admin_sync_client.canonicaldevice_list()
        assert res.count == 1
        admin_sync_client.canonicaldevice_get(id=canonical_device.id)
        admin_sync_client.canonicaldevice_update(
            id=canonical_device.id, label='test-new-canmonical-device'
        )
        admin_sync_client.canonicaldevice_delete(id=canonical_device.id)
        # TODO
        # admin_sync_client.canonicaldevice_history(id=canonical_device.id)
