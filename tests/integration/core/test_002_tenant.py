import pytest
from netdoc_sdk.client import NetDocClient
from netdoc_sdk.exceptions import NetDocError


@pytest.mark.django_db
class TestTenant:
    async def test_tenant(self, superuser_client):
        tenant = await superuser_client.tenant_add({'name': 'test-tenant'})
        await superuser_client.tenant_list()
        await superuser_client.tenant_get(id=tenant.id)
        await superuser_client.tenant_update(id=tenant.id, name="test-new-tenant", is_active=False)
        await superuser_client.tenant_delete(id=tenant.id)
