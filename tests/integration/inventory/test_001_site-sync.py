import pytest


@pytest.mark.django_db
class TestSiteSyncClient:
    @pytest.mark.django_db(transaction=True)
    def test_site(self, admin_sync_client):
        site = admin_sync_client.site_add(name='test-site')
        res = admin_sync_client.site_list()
        assert res.count == 1
        admin_sync_client.site_get(id=site.id)
        admin_sync_client.site_update(id=site.id, name='test-new-site')
        admin_sync_client.site_delete(id=site.id)
