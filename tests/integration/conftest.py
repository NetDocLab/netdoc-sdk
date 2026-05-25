"""Shared fixtures for NetDocClient unit tests."""

import pytest
from apps.core.models import Tenant
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from netdoc_sdk.client import NetDocClient


@pytest.fixture
def superuser_client(db, live_server):
    username = 'conftest-superuser'
    password = '986629a7ca89202a3ef2ae1dd9d5fb37'
    User = get_user_model()

    # Create superuser
    user = User.objects.create_user(username=username, password=password, is_superuser=True)

    # Create token
    token, _ = Token.objects.get_or_create(user=user)

    return NetDocClient(base_url=live_server.url, token=token.key)


@pytest.fixture
def admin_client(db, live_server):
    username = 'conftest-admin'
    password = '986629a7ca89202a3ef2ae1dd9d5fb37'
    User = get_user_model()

    # Create user within a tenant
    tenant = Tenant.objects.create(name='conftest-tenant')
    user = User.objects.create_user(
        username=username, password=password, tenant=tenant, role='admin'
    )

    # Create token
    token, _ = Token.objects.get_or_create(user=user)

    return NetDocClient(base_url=live_server.url, token=token.key)


@pytest.fixture
async def admin_client_by_password(db, live_server):
    username = 'conftest-admin'
    password = '986629a7ca89202a3ef2ae1dd9d5fb37'
    User = get_user_model()

    # Create user within a tenant
    tenant = await sync_to_async(Tenant.objects.create)(name='conftest-tenant')
    await sync_to_async(User.objects.create_user)(
        username=username,
        password=password,
        tenant=tenant,
        role='admin',
    )

    client = await NetDocClient.from_credentials(
        base_url=live_server.url,
        username=username,
        password=password,
    )
    async with client:
        yield client
