import pytest


@pytest.mark.django_db
class TestFilter:
    @pytest.mark.django_db(transaction=True)
    async def test_filter_name(self, superuser_client):
        await superuser_client.tenant_add(
            name='test-tenant-01', is_active=True, max_snapshots=3
        )
        await superuser_client.tenant_add(
            name='test-tenant-02', is_active=True, max_snapshots=3
        )
        await superuser_client.tenant_add(
            name='test-tenant-03', is_active=True, max_snapshots=3
        )
        res = await superuser_client.tenant_list(name='test-tenant-01')
        assert res.count == 1

    @pytest.mark.django_db(transaction=True)
    async def test_filter_name_in(self, superuser_client):
        await superuser_client.tenant_add(
            name='test-tenant-01', is_active=True, max_snapshots=3
        )
        await superuser_client.tenant_add(
            name='test-tenant-02', is_active=True, max_snapshots=3
        )
        await superuser_client.tenant_add(
            name='test-03', is_active=True, max_snapshots=3
        )
        res = await superuser_client.tenant_list(name_in='test-tenant')
        assert res.count == 2


    @pytest.mark.django_db(transaction=True)
    async def test_filter_name_nonexistent(self, superuser_client):
        await superuser_client.tenant_add(
            name='test-tenant-01', is_active=True, max_snapshots=3
        )
        res = await superuser_client.tenant_list(name='nonexistent')
        assert res.count == 0

    @pytest.mark.django_db(transaction=True)
    async def test_filter_name_in_nonexistent(self, superuser_client):
        await superuser_client.tenant_add(
            name='test-tenant-01', is_active=True, max_snapshots=3
        )
        res = await superuser_client.tenant_list(name_in='nonexistent')
        assert res.count == 0
