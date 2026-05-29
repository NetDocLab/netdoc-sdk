import pytest


@pytest.mark.django_db
class TestProfile:
    @pytest.mark.django_db(transaction=True)
    async def test_profile(self, admin_client):
        await admin_client.profile_get()
        await admin_client.profile_update(
            password='test-password'
        )
