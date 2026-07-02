import pytest


@pytest.mark.django_db
class TestCredentialSyncClient:
    @pytest.mark.django_db(transaction=True)
    def test_credential(self, admin_sync_client):
        credential = admin_sync_client.credentials_add(label='test-credential')
        res = admin_sync_client.credentials_list()
        assert res.count == 1
        admin_sync_client.credentials_get(id=credential.id)
        admin_sync_client.credentials_update(id=credential.id, label='test-new-credential')
        admin_sync_client.credentials_delete(id=credential.id)
