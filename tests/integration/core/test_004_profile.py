import pytest


@pytest.mark.django_db
class TestUser:
    @pytest.mark.django_db(transaction=True)
    async def test_profile(self, admin_client):
        await admin_client.profile_get()
        await admin_client.profile_update(
            username='test-user', password='test-password', role='admin'
        )
