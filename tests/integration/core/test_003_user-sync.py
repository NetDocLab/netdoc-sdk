import pytest


@pytest.mark.django_db
class TestUserSyncClient:
    @pytest.mark.django_db(transaction=True)
    def test_user(self, admin_sync_client):
        user = admin_sync_client.users_add(
            username='test-user',
            password='test-password',
            is_active=True,
            role='admin',
            first_name='First',
            last_name='Last',
            email='first.last@example.com',
        )
        res = admin_sync_client.users_list()
        assert res.count == 2
        admin_sync_client.users_get(user.id)
        admin_sync_client.users_get(user.username)
        admin_sync_client.users_update(
            id=user.id,
            username='test-new-user',
            is_active=False,
            role='viewer',
            first_name='Last',
            last_name='Frist',
            email='last.first@example.com',
        )
        admin_sync_client.users_delete(id=user.id)
