import pytest


@pytest.mark.django_db
class TestCanonicalDeviceSyncClient:
    @pytest.mark.django_db(transaction=True)
    def test_canonical_device(self, admin_sync_client):
        site = admin_sync_client.sites_add(name='test-site')
        canonical_device = admin_sync_client.canonical_devices_add(
            label='test-canonical-device',
            identifiers={'hostname': 'r1'},
            site=site.id,
        )
        res = admin_sync_client.canonical_devices_list()
        assert res.count == 1
        admin_sync_client.canonical_devices_get(id=canonical_device.id)
        admin_sync_client.canonical_devices_update(
            id=canonical_device.id, label='test-new-canmonical-device'
        )
        admin_sync_client.canonical_devices_delete(id=canonical_device.id)
        # TODO
        # admin_sync_client.canonical_devices_history(id=canonical_device.id)
