import pytest


@pytest.mark.django_db
class TestProfile:
    @pytest.mark.django_db(transaction=True)
    async def test_profile(self, admin_client):
        await admin_client.users_current_get()
        await admin_client.users_current_update(password='test-password')
