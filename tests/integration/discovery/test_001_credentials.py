import pytest


@pytest.mark.django_db
class TestCredential:
    @pytest.mark.django_db(transaction=True)
    async def test_credential(self, admin_client):
        credential = await admin_client.credential_add(label='test-credential')
        res = await admin_client.credential_list()
        assert res.count == 1
        await admin_client.credential_get(id=credential.id)
        await admin_client.credential_update(id=credential.id, label='test-new-credential')
        await admin_client.credential_delete(id=credential.id)
