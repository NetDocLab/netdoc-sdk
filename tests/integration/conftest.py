"""Shared fixtures for NetDocClient integration tests.

This module provides pytest fixtures for integration tests that require a live
Django instance with a real database and authentication system. These fixtures
set up test users, tenants, and authenticated clients for various permission levels.

All fixtures interact with the live_server and database (db) fixtures provided
by pytest-django, ensuring real HTTP calls are made and database state is managed.

Fixtures:
    - superuser_client: Authenticated as superuser with full permissions
    - admin_client: Authenticated as admin within a specific tenant
    - admin_client_by_password: Admin client authenticated via username/password

Note:
    Integration tests require a Django project and Django REST framework
    with token authentication configured.
"""

import pytest
from apps.core.models import Tenant
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from netdoc_sdk.client import NetDocClient


@pytest.fixture
def superuser_client(db, live_server):
    """NetDocClient authenticated as a superuser.

    Creates a superuser with token authentication and returns an authenticated
    client pointing to the live Django test server.

    Superusers have full permissions across all tenants and all resources.
    This fixture is useful for testing functionality that requires admin access.

    Args:
        db: pytest-django database fixture for test isolation
        live_server: pytest-django live_server fixture

    Returns:
        NetDocClient: Authenticated client with superuser credentials
    """
    username = 'conftest-superuser'
    password = '986629a7ca89202a3ef2ae1dd9d5fb37'
    User = get_user_model()

    # Create superuser
    user = User.objects.create_user(username=username, password=password, is_superuser=True)

    # Create token for API authentication
    token, _ = Token.objects.get_or_create(user=user)

    return NetDocClient(base_url=live_server.url, token=token.key)


@pytest.fixture
def admin_client(db, live_server):
    """NetDocClient authenticated as a tenant admin.

    Creates an admin user within a test tenant with token authentication
    and returns an authenticated client pointing to the live Django test server.

    Tenant admins have full permissions within their assigned tenant but cannot
    access resources in other tenants. This fixture is useful for testing
    multi-tenant functionality and tenant isolation.

    Args:
        db: pytest-django database fixture for test isolation
        live_server: pytest-django live_server fixture

    Returns:
        NetDocClient: Authenticated client with admin user credentials
    """
    username = 'conftest-admin'
    password = '986629a7ca89202a3ef2ae1dd9d5fb37'
    User = get_user_model()

    # Create user within a tenant
    tenant = Tenant.objects.create(name='conftest-tenant')
    user = User.objects.create_user(
        username=username, password=password, tenant=tenant, role='admin'
    )

    # Create token for API authentication
    token, _ = Token.objects.get_or_create(user=user)

    return NetDocClient(base_url=live_server.url, token=token.key)


@pytest.fixture
async def admin_client_by_password(db, live_server):
    """Async NetDocClient authenticated via username and password.

    Creates an admin user within a test tenant and returns an authenticated
    async client authenticated via the `from_credentials()` factory method
    (username/password-based authentication).

    This fixture demonstrates password-based authentication in contrast to
    the token-based authentication of other fixtures. Useful for testing
    the credential-based authentication flow.

    Args:
        db: pytest-django database fixture for test isolation
        live_server: pytest-django live_server fixture

    Yields:
        NetDocClient: Async client authenticated via credentials

    Example:
        async def test_with_password_auth(admin_client_by_password):
            async with admin_client_by_password as client:
                result = await client.profile_read()
    """
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

    # Authenticate via credentials and return client as async context
    client = await NetDocClient.from_credentials(
        base_url=live_server.url,
        username=username,
        password=password,
    )
    async with client:
        yield client


@pytest.fixture
def collector_client(db, live_server):
    """NetDocClient authenticated as a tenant collector.

    Creates a collector user within a test tenant with token authentication
    and returns an authenticated client pointing to the live Django test server.

    Tenant collectors have write-only permissions within their assigned tenant and
    cannot access resources in other tenants. This fixture is useful for testing
    multi-tenant functionality and tenant isolation.

    Args:
        db: pytest-django database fixture for test isolation
        live_server: pytest-django live_server fixture

    Returns:
        NetDocClient: Authenticated client with admin user credentials
    """
    username = 'conftest-collector'
    password = '986629a7ca89202a3ef2ae1dd9d5fb37'
    User = get_user_model()

    # Create user within a tenant
    tenant = Tenant.objects.create(name='conftest-tenant')
    user = User.objects.create_user(
        username=username, password=password, tenant=tenant, role='collector'
    )

    # Create token for API authentication
    token, _ = Token.objects.get_or_create(user=user)

    return NetDocClient(base_url=live_server.url, token=token.key)
