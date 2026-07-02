import pytest


@pytest.mark.django_db
class TestSite:
    @pytest.mark.django_db(transaction=True)
    async def test_site(self, admin_client):
        site = await admin_client.sites_add(name='test-site')
        res = await admin_client.sites_list()
        assert res.count == 1
        await admin_client.sites_get(id=site.id)
        await admin_client.sites_update(id=site.id, name='test-new-site')
        await admin_client.sites_delete(id=site.id)
