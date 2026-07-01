import pytest


@pytest.mark.django_db
class TestTenantSyncClient:
    @pytest.mark.django_db(transaction=True)
    def test_tenant(self, superuser_sync_client):
        tenant = superuser_sync_client.tenant_add(
            name='test-tenant', is_active=True, max_snapshots=3
        )
        res = superuser_sync_client.tenant_list()
        assert res.count == 1
        superuser_sync_client.tenant_get(tenant.id)
        superuser_sync_client.tenant_get(tenant.name)
        superuser_sync_client.tenant_update(
            id=tenant.id, name='test-new-tenant', is_active=False, max_snapshots=1
        )
        superuser_sync_client.tenant_delete(id=tenant.id)
