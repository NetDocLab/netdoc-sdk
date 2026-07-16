# Source Code Reference

This guide explains the structure of the NetDoc SDK and the role of its main modules.

## Overview

The package is intentionally small and focused. The public API is exposed through a thin client layer, while the generated endpoint layer provides the concrete operations for the NetDoc HTTP API.

```text
src/netdoc_sdk/
├── __init__.py              # Package exports and top-level documentation
├── _client_base.py          # Shared request lifecycle, headers, auth, and error handling
├── client.py                # Async and sync client wrappers
├── exceptions.py            # SDK-specific exception types
└── models/
    ├── __init__.py          # Model package exports
    ├── core.py              # Shared base model and core enums
    ├── _generated_models.py # Generated Pydantic models (do not edit manually)
```

The non-generated implementation is concentrated in a handful of modules that are easy to read and extend.

---

## Architecture

### Layered Design

```text
User code
    ↓
NetDocClient / NetDocSyncClient
    ↓
_client_base._NetDocClientBase
    ↓
httpx.AsyncClient / httpx.Client
    ↓
NetDoc API
```

### Design Principles

1. **Type safety:** The SDK uses type hints throughout and Pydantic models for request and response validation.
2. **Async-first:** The primary client is designed for asyncio applications, while a sync wrapper is also provided.
3. **Clear error handling:** HTTP problems are converted into SDK-specific exceptions with useful context.
4. **Small surface area:** The base client handles common concerns once, and generated endpoint methods expose the API operations.
5. **Readable implementation:** The code is organized to make it straightforward to follow request flow and response parsing.

---

## Core Components

### 1. Client layer

The public client classes live in [src/netdoc_sdk/client.py](../src/netdoc_sdk/client.py). They provide the main entry points for applications:

- `NetDocClient` for asyncio-based usage
- `NetDocSyncClient` for synchronous environments

Both classes inherit shared logic from [_client_base.py](../src/netdoc_sdk/_client_base.py), including:

- base URL normalization
- header construction
- request parameter cleanup
- response parsing
- exception translation

### 2. Shared request base

The shared base class in [_client_base.py](../src/netdoc_sdk/_client_base.py) is responsible for the request lifecycle. It ensures that each call:

1. builds the correct API path,
2. includes authentication and tenant headers,
3. cleans query parameters,
4. sends the request with `httpx`,
5. maps non-success responses to SDK exceptions,
6. deserializes successful payloads into Pydantic models.

### 3. Exceptions

The exception hierarchy in [src/netdoc_sdk/exceptions.py](../src/netdoc_sdk/exceptions.py) keeps failures explicit and inspectable. Common cases include:

- `AuthenticationError` for 401 responses
- `PermissionDeniedError` for 403 responses
- `NotFoundError` for 404 responses
- `ValidationError` for 400 responses
- `RateLimitError` for 429 responses
- `ServerError` for 5xx responses
- `ConnectionError` for network-level failures

### 4. Pydantic models

The models package in [src/netdoc_sdk/models](../src/netdoc_sdk/models) contains request and response schemas. The shared base class in [src/netdoc_sdk/models/core.py](../src/netdoc_sdk/models/core.py) is responsible for tolerating additional API fields while logging unexpected values.

---

## Request Flow

A typical request follows this flow:

```text
1. Application calls a public client method such as snapshots_list().
2. The method delegates to the shared request implementation.
3. The request layer builds headers and paths, then sends the HTTP call.
4. Non-success responses are converted into SDK exceptions.
5. Success responses are validated and returned as typed Pydantic models.
```

---

## Best Practices

### Use the context manager for the async client

```python
async with NetDocClient(base_url="https://netdoc.example.com", token="token") as client:
    await client.snapshots_list()
```

### Handle errors explicitly

```python
try:
    await client.snapshots_retrieve("missing-id")
except NotFoundError:
    print("The requested resource was not found.")
except ValidationError as exc:
    print(exc.errors)
```

### Prefer typed models

```python
snapshot = await client.snapshots_retrieve("snapshot-id")
print(snapshot.label)
```

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
