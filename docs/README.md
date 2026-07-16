# NetDoc SDK

[![Python Version](https://img.shields.io/badge/python-3.12+-blue)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/netdoc-sdk.svg)](https://pypi.org/project/netdoc-sdk/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Async Python SDK for NetDoc's `/api/v1` API. It provides a type-safe client for network discovery, inventory management, and topology queries, with both asynchronous and synchronous interfaces.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Features](#features)
- [API Reference](#api-reference)
- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Source Code](#source-code)
- [Contributing](#contributing)

## Installation

### Via pip (PyPI)

```bash
pip install netdoc-sdk
```

### Development version

```bash
git clone https://github.com/netdoclab/netdoc-sdk.git
cd netdoc-sdk
pip install -e .
```

## Quick Start

Basic usage with the async client:

```python
import asyncio
from netdoc_sdk import NetDocClient

async def main():
    # Create client and connect
    async with NetDocClient("https://netdoc.example.com", token="your-api-token") as client:
        # List snapshots
        snapshots = await client.snapshots_list()
        print(f"Found {len(snapshots)} snapshots")

        # Get a specific snapshot
        snapshot = await client.snapshots_retrieve(id="snapshot-1")
        print(f"Snapshot: {snapshot.label}")

asyncio.run(main())
```

### Creating Network Topology

Build and submit network snapshots with the fluent builder API:

```python
import asyncio
from netdoc_sdk import NetDocClient, DeviceBuilder, SnapshotBuilder

async def main():
    async with NetDocClient("https://netdoc.example.com", token="your-api-token") as client:
        # Build topology
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

        # Submit to server
        result = await client.snapshots_create(snapshot)
        print(f"Created snapshot: {result.id}")

asyncio.run(main())
```

### Querying Network Data

```python
async with NetDocClient(base_url, token=token) as client:
    # List all devices in a snapshot
    devices = await client.devices_list(snapshot="snapshot-id", page_size=50)

    # Get topology graph
    topology = await client.get_topology_graph(
        snapshot="snapshot-id",
        include_endpoints=True
    )

    # Query specific device
    device = await client.devices_retrieve(id="device-1")
    interfaces = await client.devices_interfaces_list(device=device.id)

    # Fetch L2 topology
    vlans = await client.vlan_list(snapshot="snapshot-id")
    mac_table = await client.mac_entry_list(snapshot="snapshot-id")
```

## Features

✅ **Full API Coverage** - Every OpenAPI operation exposed as a method
✅ **Async/Await** - Modern async/await syntax for non-blocking I/O
✅ **Type Safe** - Full type hints and IDE autocomplete support
✅ **Builder Pattern** - Fluent API for constructing complex objects
✅ **Error Handling** - Structured exceptions with status codes and details
✅ **Pagination** - Automatic page size handling for list operations
✅ **Flexible Auth** - Token-based or username/password authentication
✅ **Multi-tenant** - Support for tenant scoping with `tenant_id`
✅ **Connection Pooling** - Efficient HTTP connection reuse
✅ **Comprehensive Docs** - Inline docstrings and examples

## API Reference

### Discovery & Snapshots

```python
# Snapshot management
await client.snapshots_list()
await client.snapshots_create(snapshot)
await client.snapshots_retrieve(id="...")
await client.snapshots_latest_retrieve()
await client.snapshots_pin_create(id="...")
await client.snapshots_unpin_create(id="...")

# Device management
await client.devices_list(snapshot="...", page_size=50)
await client.devices_create(snapshot, device)
await client.devices_retrieve(id="...")
await client.devices_create_many_create(snapshot, devices)

# Device details
await client.devices_interfaces_list(device="...")
await client.devices_routes_list(device="...")
```

### Network Inventory

Query and explore network elements:

```python
# VLANs, IP addresses, routes
await client.vlan_list(snapshot="...")
await client.ip_address_list(snapshot="...")
await client.route_list(snapshot="...")

# MAC and ARP
await client.mac_entry_list(snapshot="...")
await client.arp_entry_list(snapshot="...")

# Endpoints
await client.endpoint_list(snapshot="...")
await client.canonical_endpoint_list()

# VRF routing
await client.vrf_list(snapshot="...")
```

### Topology

Analyze network topology and connections:

```python
# Topology graph
await client.get_topology_graph(snapshot="...", include_endpoints=True)

# Device connections
await client.device_connection_list(snapshot="...")

# Tunnel connections
await client.tunnel_connection_list(snapshot="...")

# Endpoint connections
await client.endpoint_connection_list(snapshot="...")

# L2 domain lookup
await client.l2_domain_lookup(snapshot="...", vlan=10)
```

### Core / Tenants

Manage credentials, users, and access:

```python
# Credentials
await client.credential_list()
await client.credential_create(credential)

# Tenants
await client.tenant_list()
await client.tenant_create(tenant)

# Users
await client.user_list()
await client.user_create(user)

# Tokens
await client.token_list()
await client.token_create(token)

# Profile
await client.profile_read()
```

Base URL handling:

- `base_url` accepts server root: `https://netdoc.example.com`
- Or API endpoint: `https://netdoc.example.com/api/v1`
- Client automatically normalizes both forms

### Friendly Aliases

Common operations have shorter aliases:

```python
# Long form
await client.snapshots_list()
await client.snapshots_create(snapshot)
await client.snapshots_retrieve(id="...")

# Short aliases (equivalent)
await client.list_snapshots()
await client.create_snapshot(snapshot)
await client.get_snapshot("...")

# More aliases
await client.list_devices()
await client.create_device(...)
await client.get_topology_graph(...)
```

## Authentication

### Token Authentication

Recommended for production use:

```python
client = NetDocClient(
    base_url="https://netdoc.example.com",
    token="your-api-token"
)
```

Tokens are sent as `Authorization: Token <token>` header.

### Username/Password Authentication

Authenticate with credentials:

```python
client = await NetDocClient.from_credentials(
    base_url="https://netdoc.example.com",
    username="collector",
    password="secret",
)
```

### Tenant Scoping

For superuser access across tenants:

```python
client = NetDocClient(
    base_url="https://netdoc.example.com",
    token="admin-token",
    tenant_id="tenant-uuid",  # Sent as X-Tenant-ID header
)
```

### Custom Headers

Add custom headers to all requests:

```python
client = NetDocClient(
    base_url="...",
    token="...",
    headers={
        "X-Custom-Header": "value",
        "X-Request-ID": "12345",
    }
)
```

## Error Handling

### Exception Types

```python
from netdoc_sdk.exceptions import (
    NetDocError,              # Base exception
    AuthenticationError,      # 401 Unauthorized
    PermissionDeniedError,    # 403 Forbidden
    NotFoundError,            # 404 Not Found
    ValidationError,          # 400 Bad Request
    ConflictError,            # 409 Conflict
    RateLimitError,           # 429 Too Many Requests
    ServerError,              # 500+ Server Error
    ConnectionError,          # Network/connection error
)
```

### Handling Errors

```python
from netdoc_sdk import NotFoundError, ValidationError

try:
    snapshot = await client.snapshots_retrieve("missing-id")
except NotFoundError as exc:
    print(f"Not found: {exc.detail}")
    print(f"Status: {exc.status_code}")
except ValidationError as exc:
    print(f"Validation errors: {exc.errors}")
except Exception as exc:
    print(f"Unexpected error: {exc}")
```

### Error Details

All SDK exceptions include:

```python
try:
    await client.device_create(snapshot, device)
except ValidationError as exc:
    exc.status_code  # HTTP status (400)
    exc.detail       # Human-readable error message
    exc.errors       # Structured validation errors dict
    str(exc)         # Full error representation
```

## Advanced Usage

### Pagination

Automatic pagination for list operations:

```python
# Get all devices with automatic pagination
all_devices = []
async for device in await client.devices_list(snapshot="...", page_size=100):
    all_devices.append(device)

# Or fetch specific page
response = await client.devices_list(snapshot="...", page=2, page_size=50)
```

### Filtering

Many list operations support filtering:

```python
# Filter devices by vendor
devices = await client.devices_list(
    snapshot="snapshot-1",
    vendor="cisco",
    page_size=100,
)

# Filter snapshots by status
snapshots = await client.snapshots_list(status="completed")
```

### Response Objects

All responses are Pydantic models with type safety:

```python
snapshot = await client.snapshots_retrieve("...")
print(snapshot.id)           # IDE autocomplete
print(snapshot.label)        # Type checking
print(snapshot.created_at)   # datetime object
```

### Connection Management

Explicit connection lifecycle:

```python
# Via context manager (recommended)
async with NetDocClient(base_url, token=token) as client:
    result = await client.snapshots_list()

# Manual lifecycle
client = NetDocClient(base_url, token=token)
result = await client.snapshots_list()
await client.close()
```

## Troubleshooting

### Connection Issues

**Problem:** `ConnectionError: Failed to connect to netdoc.example.com`

**Solutions:**

- Verify server is running and accessible
- Check firewall rules and network connectivity
- Ensure HTTPS/HTTP protocol is correct
- Try with curl: `curl -H "Authorization: Token $TOKEN" https://netdoc.example.com/api/v1/snapshots/`

### Authentication Errors

**Problem:** `AuthenticationError: 401 Unauthorized`

**Solutions:**

- Verify API token is correct
- Check token hasn't expired
- Ensure token is passed correctly (not URL encoded)
- Try creating a new token in the web UI

### Validation Errors

**Problem:** `ValidationError: 400 Bad Request`

**Solutions:**

- Check error message for specific field issues
- Verify request data matches API schema
- Inspect `exc.errors` dict for per-field details
- Review example in quick start above

### Type Issues

**Problem:** `mypy or IDE errors about type mismatcements`

**Solutions:**

- Ensure SDK is installed: `pip install netdoc-sdk`
- Update IDE/mypy cache: Restart IDE or `mypy --no-incremental`
- Check Python version is 3.12+: `python --version`

## Source Code

The package is organized around a small set of clearly named modules:

- **Readable docstrings** - Public modules and classes are documented in plain English.
- **Strong typing** - Type hints are used throughout the client and model layers.
- **Clear separation of concerns** - HTTP transport, request handling, and data models are kept separate.

For detailed information about the source code structure, internal implementation, and development practices, see **[Source Code Reference](reference/netdoc_sdk.md)**.

### Key Modules

| Module | Purpose |
|--------|---------|
| `client.py` | Async and sync client implementations |
| `_client_base.py` | Shared request lifecycle, authentication, and error handling |
| `exceptions.py` | SDK-specific exception hierarchy |
| `models/` | Pydantic request and response models |

### For Developers

- **Contributing Code:** See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow, coding standards, and PR expectations.
- **Running Tests:** See the test suite under [tests](tests) for examples and regression coverage.
- **Source Architecture:** See [docs/source-code.md](reference/netdoc_sdk.md) for implementation details.

## Requirements

- **Python:** 3.12 or higher
- **Dependencies:** httpx, pydantic, python-dateutil

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Development setup
- Running tests
- Code quality standards
- Commit conventions
- Pull request process

## Support

- 📖 [Full Documentation](https://github.com/netdoclab/netdoc-sdk)
- 🐛 [Issue Tracker](https://github.com/netdoclab/netdoc-sdk/issues)
- 💬 [Discussions](https://github.com/netdoclab/netdoc-sdk/discussions)

## License

MIT License - see LICENSE file for details
