import pytest


@pytest.mark.django_db
class TestProfileSyncClient:
    @pytest.mark.django_db(transaction=True)
    def test_profile(self, admin_sync_client):
        admin_sync_client.users_current_get()
        admin_sync_client.users_current_update(password='test-password')
