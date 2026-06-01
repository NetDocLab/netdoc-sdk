import pytest


@pytest.mark.django_db
class TestUser:
    @pytest.mark.django_db(transaction=True)
    async def test_user(self, admin_client):
        user = await admin_client.user_add(
            username='test-user',
            password='test-password',
            is_active=True,
            role='admin',
            first_name='First',
            last_name='Last',
            email='first.last@example.com',
        )
        res = await admin_client.user_list()
        assert res.count == 2
        await admin_client.user_get(user.id)
        await admin_client.user_get(user.username)
        await admin_client.user_update(
            id=user.id,
            username='test-new-user',
            is_active=False,
            role='viewer',
            first_name='Last',
            last_name='Frist',
            email='last.first@example.com',
        )
        await admin_client.user_delete(id=user.id)
