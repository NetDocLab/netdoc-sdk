"""Shared fixtures for NetDocClient unit tests."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from netdoc_sdk.client import NetDocClient


@pytest.fixture(scope='session')
def live_server_url(live_server):
    return live_server.url


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.fixture
def token(user):
    t, _ = Token.objects.get_or_create(user=user)
    return t.key


@pytest.fixture
async def sdk(live_server, token):
    async with NetDocClient(base_url=live_server.url, token=token) as c:
        yield c
