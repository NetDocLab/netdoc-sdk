import pytest


@pytest.mark.django_db
class TestFilterSyncClient:
    @pytest.mark.django_db(transaction=True)
    def test_filter_name(self, superuser_sync_client):
        superuser_sync_client.tenants_add(name='test-tenant-01', is_active=True, max_snapshots=3)
        superuser_sync_client.tenants_add(name='test-tenant-02', is_active=True, max_snapshots=3)
        superuser_sync_client.tenants_add(name='test-tenant-03', is_active=True, max_snapshots=3)
        res = superuser_sync_client.tenants_list(name='test-tenant-01')
        assert res.count == 1

    @pytest.mark.django_db(transaction=True)
    def test_filter_name_in(self, superuser_sync_client):
        superuser_sync_client.tenants_add(name='test-tenant-01', is_active=True, max_snapshots=3)
        superuser_sync_client.tenants_add(name='test-tenant-02', is_active=True, max_snapshots=3)
        superuser_sync_client.tenants_add(name='test-03', is_active=True, max_snapshots=3)
        res = superuser_sync_client.tenants_list(name_in='test-tenant')
        assert res.count == 2

    @pytest.mark.django_db(transaction=True)
    def test_filter_name_nonexistent(self, superuser_sync_client):
        superuser_sync_client.tenants_add(name='test-tenant-01', is_active=True, max_snapshots=3)
        res = superuser_sync_client.tenants_list(name='nonexistent')
        assert res.count == 0

    @pytest.mark.django_db(transaction=True)
    def test_filter_name_in_nonexistent(self, superuser_sync_client):
        superuser_sync_client.tenants_add(name='test-tenant-01', is_active=True, max_snapshots=3)
        res = superuser_sync_client.tenants_list(name_in='nonexistent')
        assert res.count == 0
