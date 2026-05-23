import pytest
from netdoc_sdk.client import NetDocClient
from netdoc_sdk.exceptions import AuthenticationError


@pytest.mark.django_db
class TestAuthentication:
    @pytest.mark.django_db(transaction=True)
    async def test_unauthenticated_user(self, live_server):
        client = NetDocClient(base_url=live_server.url, token='invalid')
        with pytest.raises(AuthenticationError):
            await client.site_list()

    @pytest.mark.django_db(transaction=True)
    async def test_admin_client_by_password(self, admin_client_by_password):
        await admin_client_by_password.site_list()

    # TODO: test superuser act as admin
    # TODO: test admin cannot specify tenant
