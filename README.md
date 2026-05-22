# NetDoc SDK

Async Python SDK for the NetDoc `/api/v1` API.

## Install

```bash
pip install netdoc-sdk
```

## Quick Start

```python
import asyncio

from netdoc_sdk import DeviceBuilder, NetDocClient, SnapshotBuilder


async def main():
    async with NetDocClient("https://netdoc.example.com", token="your-api-token") as client:
        snapshot = (
            SnapshotBuilder(label="nightly", description="Nightly collection")
            .add_device(
                DeviceBuilder("switch-01", snapshot="snapshot-id")
                .vendor("cisco")
                .platform("ios-xe")
                .software_version("17.9")
                .add_vlan(10, "Users")
                .add_interface("GigabitEthernet1/0/1", switchport_mode="trunk")
                .add_ip_address("Vlan10", "10.0.10.1/24", is_primary=True)
                .add_route("0.0.0.0/0", next_hop="10.0.10.254", protocol="static")
                .build()
            )
            .add_link("switch-01", "GigabitEthernet1/0/1", "switch-02", "GigabitEthernet1/0/1")
            .build()
        )

        await client.create_snapshot(snapshot)
        devices = await client.list_devices(snapshot="snapshot-id", page_size=50)
        topology = await client.get_topology_graph(snapshot="snapshot-id", include_endpoints=True)
        return devices, topology


asyncio.run(main())
```

`base_url` may be either the server root (`https://netdoc.example.com`) or an API URL ending in
`/api/v1`; the client normalizes both forms.

## API Surface

The client exposes every OpenAPI `operationId` as an async method, for example:

- `snapshots_list`, `snapshots_create`, `snapshots_retrieve`, `snapshots_partial_update`,
  `snapshots_destroy`, `snapshots_pin_create`, `snapshots_unpin_create`,
  `snapshots_status_create`, `snapshots_latest_retrieve`
- `devices_list`, `devices_create`, `devices_retrieve`, `devices_interfaces_list`,
  `devices_routes_list`, `devices_create_many_create`
- inventory read APIs for interfaces, VRFs, VLANs, IP addresses, routes, ARP entries,
  MAC entries, endpoints, canonical devices, and canonical endpoints
- topology APIs for device connections, tunnel connections, endpoint connections,
  topology graph, and L2 domain lookup
- core APIs for credentials, tenants, users, and token creation

Friendly aliases are also available for common calls, such as `list_snapshots`,
`create_snapshot`, `get_snapshot`, `create_device`, `list_devices`, and `get_topology_graph`.

## Authentication

```python
client = await NetDocClient.from_credentials(
    "https://netdoc.example.com",
    username="collector",
    password="secret",
)
```

Token auth uses `Authorization: Token <token>`. For superuser tenant scoping, pass
`tenant_id="..."`; the client sends it as `X-Tenant-ID`.

## Errors

HTTP failures preserve `status_code`, `detail`, and the raw parsed response body:

```python
from netdoc_sdk import NotFoundError, ValidationError

try:
    await client.get_snapshot("missing")
except NotFoundError as exc:
    print(exc.status_code, exc.detail)
except ValidationError as exc:
    print(exc.errors)
```
