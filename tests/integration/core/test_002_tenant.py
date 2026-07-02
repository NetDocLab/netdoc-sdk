import pytest


@pytest.mark.django_db
class TestTenant:
    @pytest.mark.django_db(transaction=True)
    async def test_tenant(self, superuser_client):
        tenant = await superuser_client.tenants_add(
            name='test-tenant', is_active=True, max_snapshots=3
        )
        res = await superuser_client.tenants_list()
        assert res.count == 1
        await superuser_client.tenants_get(tenant.id)
        await superuser_client.tenants_get(tenant.name)
        await superuser_client.tenants_update(
            id=tenant.id, name='test-new-tenant', is_active=False, max_snapshots=1
        )
        await superuser_client.tenants_delete(id=tenant.id)
