import pytest


@pytest.mark.django_db
class TestProfileSyncClient:
    @pytest.mark.django_db(transaction=True)
    def test_profile(self, admin_sync_client):
        admin_sync_client.profile_get()
        admin_sync_client.profile_update(password='test-password')
