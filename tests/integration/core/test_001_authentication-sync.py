import pytest
from apps.core.models import Tenant
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from netdoc_sdk.client import NetDocSyncClient as NetDocClient
from netdoc_sdk.exceptions import AuthenticationError


@pytest.mark.django_db
class TestAuthenticationSyncClient:
    @pytest.mark.django_db(transaction=True)
    def test_unauthenticated_user(self, live_server):
        client = NetDocClient(base_url=live_server.url, token='invalid')
        with pytest.raises(AuthenticationError):
            client.sites_list()

    @pytest.mark.django_db(transaction=True)
    def test_admin_client_by_password(self, admin_sync_client_by_password):
        admin_sync_client_by_password.sites_list()

    @pytest.mark.django_db(transaction=True)
    def test_superuser_impersonating(self, live_server):
        username = 'conftest-admin'
        password = '986629a7ca89202a3ef2ae1dd9d5fb37'
        User = get_user_model()

        # Add tenant
        tenant = Tenant.objects.create(name='test-tenant')

        # Add superuser
        user = User.objects.create_user(
            username=username,
            password=password,
            tenant=tenant,
            role='admin',
        )

        # Generate token
        token, _ = Token.objects.get_or_create(user=user)

        client = NetDocClient(base_url=live_server.url, token=token.key)
        client.sites_list()
