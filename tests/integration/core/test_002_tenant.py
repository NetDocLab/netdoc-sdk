import pytest


@pytest.mark.django_db
class TestTenant:
    @pytest.mark.django_db(transaction=True)
    async def test_tenant(self, superuser_client):
        tenant = await superuser_client.tenant_add({'name': 'test-tenant'})
        res = await superuser_client.tenant_list()
        assert res.count == 1
        await superuser_client.tenant_get(id=tenant.id)
        await superuser_client.tenant_update(id=tenant.id, name="test-new-tenant", is_active=False)
        await superuser_client.tenant_delete(id=tenant.id)
