import pytest


@pytest.mark.django_db
class TestUser:
    @pytest.mark.django_db(transaction=True)
    async def test_user(self, admin_client):
        user = await admin_client.user_add(
            username='test-user', password='test-password', role='admin'
        )
        res = await admin_client.user_list()
        assert res.count == 2
        await admin_client.user_get(id=user.id)
        await admin_client.user_update(id=user.id, name='test-new-user', is_active=False)
        await admin_client.user_delete(id=user.id)
