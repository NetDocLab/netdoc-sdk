from asgiref.sync import sync_to_async
import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from apps.core.models import Tenant
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

    @pytest.mark.django_db(transaction=True)
    async def test_superuser_impersonating(self, live_server):
        username = 'conftest-admin'
        password = '986629a7ca89202a3ef2ae1dd9d5fb37'
        User = get_user_model()

        # Add tenant
        tenant = await sync_to_async(Tenant.objects.create)(name='test-tenant')

        # Add superuser
        user = await sync_to_async(User.objects.create_user)(
            username=username,
            password=password,
            tenant=tenant,
            role='admin',
        )

        # Generate token
        token, _ = await sync_to_async(Token.objects.get_or_create)(user=user)

        client = NetDocClient(base_url=live_server.url, token=token.key)
        await client.site_list()
