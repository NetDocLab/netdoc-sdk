import pytest
from netdoc_sdk.client import NetDocClient
from netdoc_sdk.exceptions import NetDocError, AuthenticationError


@pytest.mark.django_db
class TestAuthentication:
    async def test_unauthenticated_user(self, live_server_url):
        client = NetDocClient(base_url=live_server_url, token='invalid')
        with pytest.raises(AuthenticationError):
            await client.site_list()

    # TODO: with NetDocClient base_url and token are mandatory

    # print(live_server_url)
    # client = NetDocClient(base_url=live_server_url, token="AAA")
    # tenant = await client.tenant_add({"nome": "test"})
    # print(tenant)
    # print(type(tenant))
    # assert tenant.id is not None
    # assert tenant.name == "test"

    # async def test_tenant_add(self, sdk):
    #     tenant = await sdk.tenant_add(name="test")  # ← await obbligatorio
    #     assert tenant.id is not None
    #     assert tenant.name == "test"
