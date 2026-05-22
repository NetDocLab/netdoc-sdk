import uuid

import pytest
from factories import CredentialFactory


@pytest.mark.asyncio
class TestCredentialCreate:
    def _verify_credential(self, credential, payload=None):
        assert credential.id is not None
        if payload:
            assert credential.label == payload['label']
            assert credential.description == payload['description']
            assert credential.username == payload['username']
            assert credential.verify_cert == payload['verify_cert']
        assert not hasattr(credential, 'password')
        assert not hasattr(credential, 'secret')

    async def test_credential_create(self, admin_client):
        """Admin must be allowed to create credentials."""
        payload = CredentialFactory()
        data = await admin_client.credentials_create(**payload)
        self._verify_credential(data, payload=payload)

    async def test_credential_read_list(self, admin_client, credential_create):
        """Admin must be allowed to read credential list."""
        credential = await credential_create()
        data = await admin_client.credentials_list()
        assert data.count >= 1
        for item in data.results:
            self._verify_credential(item)

    async def test_credential_read_detail(self, admin_client, credential_create):
        """Admin must be allowed to read credential details."""
        credential = await credential_create()
        data = await admin_client.credentials_retrieve(credential.id)
        self._verify_credential(data, payload=credential.dict())

    async def test_credential_update(self, admin_client, credential_create):
        """Admin must be allowed to update credentials and persist them."""
        update_payload = {
            'label': f'sdk-test-{uuid.uuid4()}-updated',
            'description': 'Updated Credential Description',
            'username': 'admin',
            'password': 'password',
            'secret': 'secret',
            'verify_cert': False,
        }
        credential = await credential_create()
        updated_credential = await credential.update(**update_payload)
        self._verify_credential(updated_credential, payload=update_payload)

    async def test_credential_delete(self, admin_client, credential_create):
        """Admin must be allowed to delete credentials."""
        credential = await credential_create()
        await credential.delete()
