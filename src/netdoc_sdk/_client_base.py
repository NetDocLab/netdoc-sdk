"""Base class shared by the sync and async NetDoc clients.

All endpoint methods live here as plain ``def`` returning ``self._request(...)``.
This makes them transparent with respect to sync/async: when ``_request`` is a
regular method the call resolves immediately; when it is a coroutine the caller
receives that coroutine and must ``await`` it.  Either way the method body is
written exactly once.

Subclasses must implement:
    - ``_request``       (sync or async)
    - ``_make_client``   (returns httpx.Client or httpx.AsyncClient)
    - context manager protocol (``__enter__``/``__exit__`` or async equivalents)
    - ``from_credentials`` classmethod
"""

import logging
from collections.abc import Iterable, Mapping
from typing import Any

import httpx
from pydantic import BaseModel

from netdoc_sdk._generated_endpoints import JsonMapping, _GeneratedEndpoints
from netdoc_sdk.exceptions import (
    AuthenticationError,
    MethodNotAllowedError,
    NetDocError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    ValidationError,
)

logger = logging.getLogger('netdoc_sdk')


class _NetDocClientBase(_GeneratedEndpoints):
    """Shared logic for both the sync and async NetDoc clients."""

    api_prefix = 'api/v1'

    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        *,
        client_kwargs: Mapping[str, Any] | None = None,
        cookies: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        tenant_id: str | None = None,
        max_retries: int = 5,
        timeout: float = 30.0,
        transport: Any | None = None,
        verify: bool = True,
    ) -> None:
        self.base_url = self._normalize_base_url(base_url)
        self.client_kwargs = dict(client_kwargs or {})
        self.cookies = dict(cookies or {})
        self.extra_headers = dict(headers or {})
        self.tenant_id = tenant_id
        self.max_retries = max_retries
        self.timeout = timeout
        self.token = token
        self.transport = transport
        self.verify = verify

        if self.verify is False:
            logger.warning('TLS certificate verification is disabled for %s', self.base_url)

    # ------------------------------------------------------------------
    # Helpers — pure logic, no I/O
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        url = httpx.URL(base_url.rstrip('/') or 'http://localhost')
        path = url.path.rstrip('/')
        if path.endswith('/api/v1'):
            path = path[: -len('/api/v1')]
        return str(url.copy_with(path=(path or '/'))).rstrip('/')

    def _build_headers(self) -> dict[str, str]:
        """Assemble the default headers for a new HTTP client instance."""
        headers: dict[str, str] = {'Accept': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Token {self.token}'
        if self.tenant_id:
            headers['X-Tenant-ID'] = self.tenant_id
        headers.update(self.extra_headers)
        return headers

    def _api_path(self, path: str) -> str:
        path = path.lstrip('/')
        if path.startswith(f'{self.api_prefix}/'):
            return path
        return f'{self.api_prefix}/{path}'

    @staticmethod
    def _clean_params(params: Mapping[str, Any] | None) -> dict[str, Any] | None:
        if not params:
            return None
        cleaned = {k: v for k, v in params.items() if v is not None}
        return cleaned or None

    @staticmethod
    def _serialize_body(body: JsonMapping | None = None, **fields: Any) -> dict[str, Any] | None:
        merged: dict[str, Any] = {}
        if body is not None:
            if isinstance(body, BaseModel):
                merged.update(body.model_dump(mode='json', exclude_unset=True, exclude_none=True))
            else:
                merged.update(dict(body))
        merged.update({k: v for k, v in fields.items() if v is not None})
        return merged or None

    @staticmethod
    def _request_headers(method: str, extra: Mapping[str, str] | None) -> dict[str, str]:
        """Build per-request headers (Content-Type + any caller overrides)."""
        headers: dict[str, str] = {}
        if method.upper() in ('POST', 'PUT', 'PATCH'):
            headers['Content-Type'] = 'application/json'
        if extra:
            headers.update(extra)
        return headers

    @staticmethod
    def _expected_set(
        expected_status: int | Iterable[int] | None,
    ) -> set[int]:
        if expected_status is None:
            return set()
        if isinstance(expected_status, int):
            return {expected_status}
        return set(expected_status)

    @staticmethod
    def _is_ok(status_code: int, expected: set[int]) -> bool:
        if not expected:
            return 200 <= status_code < 300
        return status_code in expected

    def _parse_retry_after(self, value: str | None) -> float:
        """Return the number of seconds to wait before retrying a 429 response."""
        default = 1.0
        if not value:
            logger.warning('Retry-After header missing, using %.1fs', default)
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning('Retry-After value %r is invalid, using %.1fs', value, default)
            return default

    def _raise_for_error(self, response: httpx.Response) -> None:
        """Translate a non-successful HTTP response into an SDK exception."""
        body: Any
        try:
            body = response.json()
        except ValueError:
            body = {'detail': response.text}

        detail = body.get('detail') if isinstance(body, dict) else body
        message = detail if isinstance(detail, str) else f'API error: {response.status_code}'

        if response.status_code == 400:
            raise ValidationError(message, errors=body, detail=detail, body=body)
        if response.status_code == 401:
            raise AuthenticationError(message, detail=detail, body=body)
        if response.status_code == 403:
            raise PermissionDeniedError(message, detail=detail, body=body)
        if response.status_code == 404:
            raise NotFoundError(message, detail=detail, body=body)
        if response.status_code == 405:
            raise MethodNotAllowedError(message, detail=detail, body=body)
        if response.status_code == 429:
            retry_after = response.headers.get('Retry-After')
            raise RateLimitError(
                retry_after=(int(retry_after) if retry_after and retry_after.isdigit() else None),
                detail=detail,
                body=body,
            )
        if response.status_code >= 500:
            raise ServerError(message, status_code=response.status_code, detail=detail, body=body)
        raise NetDocError(message, status_code=response.status_code, detail=detail, body=body)

    def _parse_response(
        self,
        response: httpx.Response,
        response_model: Any,
        expected: set[int],
    ) -> Any:
        """Deserialise a successful response into the expected model.

        Extracted from ``_request`` so both sync and async implementations can
        reuse the same deserialization and edge-case logic.
        """
        from pydantic import TypeAdapter

        if not response_model and not response.content:
            return None

        if response.status_code == 204 and len(expected) > 1:
            # Endpoint may legitimately return 204 with no body.
            return None

        if response_model and not response.content:
            req = response.request
            raise ValidationError(
                f'Expected {response_model.__name__} but got nothing',
                errors='',
                detail=f'{req.method} {req.url}',
                body='',
            )

        return TypeAdapter(response_model).validate_python(response.json())
