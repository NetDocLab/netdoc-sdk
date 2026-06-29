# Source Code Reference

This guide explains the structure and implementation of the NetDoc SDK source code.

## Overview

The SDK is organized into clear modules:

```text
src/netdoc_sdk/
├── __init__.py       # Package exports
├── client.py         # Main NetDocClient class (773 lines)
├── exceptions.py     # Exception hierarchy (270+ lines)
└── models/           # Pydantic models
    ├── __init__.py   # Models documentation
    ├── core.py       # User, tenant, token models (196 lines)
    ├── discovery.py  # Credential, collector, job models (249 lines)
    ├── inventory.py  # Site, device, interface models (131 lines)
    └── snapshots.py  # Snapshot models (36 lines)
```

**Total:** 1,537 lines of production code with comprehensive docstrings and type hints.

---

## Architecture

### Layered Design

```text
User Code
    ↓
NetDocClient (public async methods)
    ↓
_request() (HTTP abstraction)
    ↓
httpx.AsyncClient (HTTP transport)
    ↓
Server API
```

### Design Principles

1. **Type Safety:** Full type hints throughout, Pydantic for runtime validation
2. **Async-First:** All I/O operations are truly async (no blocking calls)
3. **Error Clarity:** Rich exception hierarchy preserving HTTP context
4. **Lazy Initialization:** Client only created when needed (context manager or `.client` property)
5. **Simplicity:** No complex abstractions, straightforward request-response flow

---

## Core Components

### 1. NetDocClient (client.py)

The main client class that provides a complete async interface to the NetDoc API.

**Initialization:**

```python
# Token-based authentication (recommended)
client = NetDocClient(
    base_url="https://netdoc.example.com",
    token="your-api-token",
)

# Password-based authentication
client = await NetDocClient.from_credentials(
    base_url="https://netdoc.example.com",
    username="user",
    password="pass",
)

# Multi-tenant (superuser)
client = NetDocClient(
    base_url="...",
    token="admin-token",
    tenant_id="tenant-uuid",
)
```

**Lifecycle Management:**

```python
# Recommended: use context manager
async with NetDocClient(...) as client:
    await client.snapshots_list()
# Client automatically closed

# Or manage manually
client = NetDocClient(...)
data = await client.snapshots_list()
await client.close()
```

**Key Methods:**

| Method | Type | Purpose |
|--------|------|---------|
| `__init__()` | Constructor | Initialize client with configuration |
| `__aenter__()` / `__aexit__()` | Async context manager | Lifecycle management |
| `from_credentials()` | Class method | Create client from username/password |
| `client` property | Property | Lazy-initialize internal httpx.AsyncClient |
| `close()` | Async method | Close and cleanup internal client |
| `_request()` | Internal async | Low-level HTTP request with error handling |
| `_normalize_base_url()` | Static | Normalize base URL formats |
| `_clean_params()` | Static | Filter None values from query params |
| `_serialize_body()` | Static | Merge and serialize request body |

**Public API Methods:**

The client exposes every OpenAPI operationId. Examples:

- Snapshots: `snapshots_list()`, `snapshots_create()`, `snapshots_retrieve()`, `snapshots_partial_update()`, `snapshots_destroy()`
- Devices: `devices_list()`, `devices_create()`, `devices_retrieve()`, `devices_interfaces_list()`
- Credentials: `credential_list()`, `credential_create()`, `credential_update()`
- Users: `user_list()`, `user_create()`, `user_profile_read()`, `user_profile_update()`
- Tokens: `token_list()`, `token_add()`

See README.md for complete API reference.

### 2. Exception Hierarchy (exceptions.py)

Rich exception types with HTTP context preservation:

```python
NetDocError (base)
├── AuthenticationError (401)
├── PermissionDeniedError (403)
├── NotFoundError (404)
├── MethodNotAllowedError (405)
├── ValidationError (400)
├── RateLimitError (429)
├── ServerError (5xx)
└── ConnectionError (network)
```

Each exception preserves:

- `status_code`: HTTP status (or None for ConnectionError)
- `detail`: Server error detail message
- `body`: Full parsed response
- `message`: Human-readable message

Example:

```python
try:
    await client.snapshots_retrieve("missing")
except NotFoundError as e:
    print(f"404 Not Found: {e.detail}")
    print(f"Full response: {e.body}")
except ValidationError as e:
    print(f"Validation failed: {e.errors}")  # Per-field errors
```

### 3. Pydantic Models (models/)

All models follow consistent patterns:

**Base Classes:**

```python
class APIModel(BaseModel):
    """Base for all models with extra field tolerance."""
    # Forbids extra fields in tests, ignores in production
    # Logs warnings for unexpected fields (API version mismatch)
```

**Model Types:**

| Type | Example | Purpose |
|------|---------|---------|
| Detail (Read) | `SnapshotDetail`, `SiteDetail` | Full resource representation |
| Create (Write) | `SnapshotCreate`, `SiteCreate` | Request payload for creation |
| Update (Write) | `SnapshotUpdate`, `SiteUpdate` | Request payload for updates |
| Paginated (List) | `PaginatedSnapshotList` | List responses with metadata |
| Enum | `JobStatus`, `Severity` | Predefined values |

**Key Features:**

- Type hints for all fields
- Automatic coercion (str → UUID, str → datetime)
- `populate_by_name=True` for field aliases
- `exclude_none=True` when serializing (don't send null fields)
- `exclude_unset=True` for partial updates (only send changed fields)

Example:

```python
from netdoc_sdk.models.snapshots import SnapshotDetail, SnapshotUpdate

# Read: Full resource from API
snapshot: SnapshotDetail = await client.snapshots_retrieve("id")
print(snapshot.id, snapshot.label, snapshot.created_at)

# Create: Build request
from netdoc_sdk.models.snapshots import SnapshotCreate
data = SnapshotCreate(label="nightly", description="Auto-generated")
result = await client.snapshots_create(data)

# Update: Partial fields only
update = SnapshotUpdate(label="updated")
await client.snapshots_partial_update("id", update)
```

---

## Request Flow

How a typical request is processed:

```text
1. User calls: await client.snapshots_list(page_size=50)

2. Generated method calls:
   await self._request(
       method='GET',
       path='snapshots/',
       params={'page_size': 50},
       response_model=PaginatedSnapshotList,
   )

3. _request() method:
   a) Clean query params (filter None values)
   b) Build headers (auth, tenant, custom)
   c) Send HTTP request via httpx
   d) Handle status codes → raise exceptions
   e) Parse response with Pydantic model
   f) Return deserialized object

4. User receives: PaginatedSnapshotList instance
   - Fully typed
   - Validated
   - Ready to use
```

---

## Error Handling

The SDK converts HTTP errors into specific exception types:

| Status | Exception | When |
|--------|-----------|------|
| 400 | ValidationError | Request validation failed |
| 401 | AuthenticationError | Token missing/invalid/expired |
| 403 | PermissionDeniedError | User lacks permission |
| 404 | NotFoundError | Resource doesn't exist |
| 405 | MethodNotAllowedError | HTTP method not supported |
| 429 | RateLimitError | Rate limit exceeded |
| 500+ | ServerError | Server-side error |
| Network | ConnectionError | Can't reach server |

Example error handling:

```python
try:
    await client.snapshots_retrieve("missing")
except NotFoundError:
    print("Snapshot not found")
except PermissionDeniedError:
    print("You don't have permission")
except ServerError as e:
    print(f"Server error {e.status_code}: {e.detail}")
    # Might be transient, could retry with backoff
except ConnectionError:
    print("Network error, can't reach server")
```

---

## Configuration Options

### NetDocClient Init Parameters

```python
NetDocClient(
    base_url: str,                    # Server URL (required)
    token: str | None = None,          # API token for auth

    # Advanced options (keyword-only)
    client_kwargs: dict | None = None, # Extra httpx.AsyncClient kwargs
    cookies: dict | None = None,       # HTTP cookies to send
    headers: dict | None = None,       # Custom headers
    tenant_id: str | None = None,      # Tenant ID for multi-tenant
    max_retries: int = 5,              # Max retry attempts
    timeout: float = 30.0,             # Request timeout (seconds)
    transport: httpx.AsyncBaseTransport | None = None,  # Custom transport
)
```

**Common Configurations:**

```python
# Basic
client = NetDocClient(base_url="...", token="...")

# With custom headers
client = NetDocClient(
    base_url="...",
    token="...",
    headers={"X-Request-ID": "my-id"},
)

# With client customization
client = NetDocClient(
    base_url="...",
    token="...",
    timeout=60.0,  # Longer timeout
    max_retries=10,  # More retries
    client_kwargs={"limits": httpx.Limits(max_connections=10)},
)

# Multi-tenant (admin user)
client = NetDocClient(
    base_url="...",
    token="admin-token",
    tenant_id="tenant-uuid",
)
```

---

## Best Practices

### 1. Always Use Context Manager

```python
# ✅ Good: Automatic cleanup
async with NetDocClient(base_url, token) as client:
    await client.snapshots_list()

# ❌ Avoid: Manual cleanup is easy to forget
client = NetDocClient(base_url, token)
try:
    await client.snapshots_list()
finally:
    await client.close()
```

### 2. Handle Errors Specifically

```python
# ✅ Good: Specific error handling
try:
    snapshot = await client.snapshots_retrieve("id")
except NotFoundError:
    # Handle missing resource
except ValidationError as e:
    # Handle validation errors with detailed info
except ServerError:
    # Might retry
except ConnectionError:
    # Handle network issues
```

### 3. Use Type Hints

```python
# ✅ Good: IDE autocomplete and type checking
async def process_snapshots(client: NetDocClient) -> list[str]:
    snapshots: PaginatedSnapshotList = await client.snapshots_list()
    return [s.label for s in snapshots.results]

# ❌ Avoid: No type information
async def process_snapshots(client):
    snapshots = await client.snapshots_list()
    return [s.label for s in snapshots.results]
```

### 4. Pagination

```python
# ✅ Good: Handle pagination
async for page in await client.snapshots_list(page_size=100):
    # Process each page

# ✅ Also good: Get specific page
result = await client.snapshots_list(page=2, page_size=50)
```

### 5. Request Body Construction

```python
from netdoc_sdk.models.snapshots import SnapshotCreate

# ✅ Good: Use model
snapshot = SnapshotCreate(label="nightly")
await client.snapshots_create(snapshot)

# ✅ Also good: Use kwargs
await client.snapshots_create(label="nightly")

# ✅ Dict also works (less safe)
await client.snapshots_create({"label": "nightly"})
```

---

## Internal Implementation Details

### URL Normalization

The `_normalize_base_url()` method handles various URL formats:

```python
NetDocClient("http://example.com")           # ✓
NetDocClient("http://example.com/")          # ✓ Trailing slash removed
NetDocClient("http://example.com/api/v1")    # ✓ /api/v1 removed
NetDocClient("http://example.com/api/v1/")   # ✓ Both removed
```

All normalize to: `http://example.com`

### Parameter Cleaning

The `_clean_params()` method filters None values:

```python
_clean_params({"a": 1, "b": None, "c": ""})
# Returns: {"a": 1, "c": ""}

_clean_params({"a": None, "b": None})
# Returns: None (empty dict becomes None)

_clean_params(None)
# Returns: None
```

This prevents `?b=None` in URLs and empty query strings.

### Body Serialization

The `_serialize_body()` method handles merging and validation:

```python
# Merge dict + kwargs
_serialize_body({"name": "a"}, code="XY")
# Returns: {"name": "a", "code": "XY"}

# Pydantic model → dict
model = SiteCreate(name="Site A")
_serialize_body(model)
# Returns: {"name": "Site A"}

# None values filtered
_serialize_body({"name": "a"}, code=None)
# Returns: {"name": "a"} (code excluded)

_serialize_body(None)
# Returns: None (empty body)
```

---

## Performance Considerations

### Connection Pooling

The internal `httpx.AsyncClient` maintains a connection pool for efficient reuse:

```python
async with NetDocClient(...) as client:
    # First request: creates connection
    await client.snapshots_list()

    # Subsequent requests: reuse connection
    await client.devices_list()

    # Multiple in parallel: uses pool
    await asyncio.gather(
        client.snapshots_list(),
        client.devices_list(),
    )
```

### Request Limits

Configure connection pool size for your workload:

```python
import httpx

client = NetDocClient(
    base_url="...",
    token="...",
    client_kwargs={
        "limits": httpx.Limits(
            max_connections=10,      # Max concurrent connections
            max_keepalive_connections=5,  # Max idle connections
        )
    }
)
```

### Timeout Configuration

Set appropriate timeouts for your use case:

```python
# Fast, interactive use (default)
client = NetDocClient(..., timeout=30.0)

# Slow, bulk operations
client = NetDocClient(..., timeout=300.0)

# No timeout (careful!)
client = NetDocClient(..., timeout=None)
```

---

## Testing the SDK

For testing your code that uses the SDK:

**Unit tests (mock the client):**

```python
from unittest.mock import AsyncMock
from netdoc_sdk import NetDocClient

async def test_my_code():
    mock_client = AsyncMock(spec=NetDocClient)
    mock_client.snapshots_list.return_value = [...]

    result = await my_function(mock_client)
    assert result == ...
```

**Integration tests (use live server):**

See `tests/integration/` for examples using `pytest-django` fixtures.

---

## Contributing to Source Code

See CONTRIBUTING.md for detailed guidelines on:

- Code quality standards (type hints, docstrings)
- Running tests (`make test`)
- Code formatting (`ruff format`, `ruff check`)
- Type checking (`mypy src/`)
- Commit conventions

When modifying source code:

1. **Preserve type hints** - All function signatures must be typed
2. **Add docstrings** - Google style for all public APIs
3. **Add tests** - Every feature/fix needs tests
4. **Update models** - If API contract changes, update Pydantic models
5. **Update docs** - If user-facing behavior changes, update README/CONTRIBUTING

---

## References

- [NetDoc API Documentation](https://github.com/netdoclab/netdoc)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [httpx Documentation](https://www.python-httpx.org/)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)
