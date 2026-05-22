"""Async HTTP client for the NetDoc OpenAPI surface."""

from collections.abc import Iterable, Mapping
from typing import Any
import httpx
from pydantic import BaseModel, TypeAdapter
from netdoc_sdk.exceptions import (
    AuthenticationError,
    ConnectionError,
    MethodNotAllowedError,
    NetDocError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from netdoc_sdk.models.core import (
    AuditLogDetail,
    PaginatedAuditLogList,
    PaginatedTenantList,
    PaginatedUserList,
    TenantCreate,
    TenantDetail,
    TenantUpdate,
    TokenDetail,
    TokenRequest,
    UserCreate,
    UserDetail,
    UserUpdate,
)
from netdoc_sdk.models.snapshots import (
    PaginatedSnapshotList,
    SnapshotDetail,
    SnapshotUpdate,
)


JsonMapping = Mapping[str, Any] | BaseModel


class NetDocClient:
    """Async client for endpoint published under `/api/v1`."""

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
        timeout: float = 30.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        self._client: httpx.AsyncClient | None = None
        self.base_url = self._normalize_base_url(base_url)
        self.client_kwargs = dict(client_kwargs or {})
        self.cookies = dict(cookies or {})
        self.extra_headers = dict(headers or {})
        self.tenant_id = tenant_id
        self.timeout = timeout
        self.token = token
        self.transport = transport

    async def __aenter__(self) -> 'NetDocClient':
        self._client = self._make_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    @classmethod
    async def from_credentials(
        cls,
        base_url: str,
        password: str,
        username: str,
        **kwargs: Any,
    ) -> 'NetDocClient':
        """Create a token with `/api/v1/tokens/` and return an authenticated client."""

        async with cls(base_url=base_url, **kwargs) as bootstrap:
            token = await bootstrap.tokens_create(username=username, password=password)
        return cls(base_url=base_url, token=token.token, **kwargs)

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        url = httpx.URL(base_url.rstrip('/') or 'http://localhost')
        path = url.path.rstrip('/')
        if path.endswith('/api/v1'):
            path = path[: -len('/api/v1')]
        return str(url.copy_with(path=(path or '/'))).rstrip('/')

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = self._make_client()
        return self._client

    def _make_client(self) -> httpx.AsyncClient:
        headers = {'Accept': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Token {self.token}'
        if self.tenant_id:
            headers['X-Tenant-ID'] = self.tenant_id
        headers.update(self.extra_headers)
        return httpx.AsyncClient(
            base_url=self.base_url,
            cookies=self.cookies,
            headers=headers,
            timeout=self.timeout,
            transport=self.transport,
            **self.client_kwargs,
        )

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

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

    async def _request(
        self,
        method: str,
        path: str,
        *,
        content: bytes | str | None = None,
        expected_status: int | Iterable[int] | None = None,
        headers: Mapping[str, str] | None = None,
        json: JsonMapping | None = None,
        params: Mapping[str, Any] | None = None,
        response_model: Any = None,
    ) -> Any:
        expected = None
        if expected_status is not None:
            expected = (
                {expected_status} if isinstance(expected_status, int) else set(expected_status)
            )

        try:
            response = await self.client.request(
                content=content,
                headers=dict(headers or {}),
                json=self._serialize_body(json) if json is not None else None,
                method=method,
                params=self._clean_params(params),
                url=self._api_path(path),
            )
        except (httpx.ConnectError, httpx.NetworkError) as exc:
            raise ConnectionError(f'Failed to connect: {exc}') from exc
        except httpx.TimeoutException as exc:
            raise ConnectionError(f'Request timed out: {exc}') from exc

        if expected is None:
            ok = 200 <= response.status_code < 300
        else:
            ok = response.status_code in expected
        if not ok:
            self._raise_for_error(response)

        if response.status_code == 204 or not response.content:
            return None

        data = response.json()
        if response_model is None:
            return data
        return TypeAdapter(response_model).validate_python(data)

    def _raise_for_error(self, response: httpx.Response) -> None:
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


    # ---------------------------------------------------------------------------
    # core.Tenant
    # ---------------------------------------------------------------------------


    async def tenant_add(
        self, data: JsonMapping | TenantCreate | None = None, **fields: Any
    ) -> TenantDetail:
        return await self._request(
            'POST',
            'tenants/',
            json=self._serialize_body(data, **fields),
            expected_status=201,
            response_model=TenantDetail,
        )

    async def tenant_list(self, **params: Any) -> PaginatedTenantList:
        return await self._request(
            'GET', 'tenants/', params=params, response_model=PaginatedTenantList
        )

    async def tenant_get(self, id: str) -> TenantDetail:
        return await self._request('GET', f'tenants/{id}/', response_model=TenantDetail)

    async def tenants_update(
        self, id: str, data: JsonMapping | TenantUpdate | None = None, **fields: Any
    ) -> TenantDetail:
        return await self._request(
            'PATCH',
            f'tenants/{id}/',
            json=self._serialize_body(data, **fields),
            response_model=TenantDetail,
        )

    async def tenant_rm(self, id: str) -> None:
        return await self._request('DELETE', f'tenants/{id}/', expected_status=204)

    async def tenant_current(self) -> TenantDetail:
        return await self._request('GET', 'tenants/current/', response_model=TenantDetail)


    # ---------------------------------------------------------------------------
    # core.User
    # ---------------------------------------------------------------------------


    async def user_add(
        self, data: JsonMapping | UserCreate | None = None, **fields: Any
    ) -> UserDetail:
        return await self._request(
            'POST',
            'users/',
            json=self._serialize_body(data, **fields),
            expected_status=201,
            response_model=UserDetail,
        )

    async def user_list(self, **params: Any) -> PaginatedUserList:
        return await self._request(
            'GET', 'users/', params=params, response_model=PaginatedUserList
        )

    async def user_get(self, id: str) -> UserDetail:
        return await self._request('GET', f'users/{id}/', response_model=UserDetail)

    async def user_update(
        self, id: str, data: JsonMapping | UserUpdate | None = None, **fields: Any
    ) -> UserDetail:
        return await self._request(
            'PATCH',
            f'users/{id}/',
            json=self._serialize_body(data, **fields),
            response_model=UserDetail,
        )

    async def user_rm(self, id: str) -> None:
        return await self._request('DELETE', f'users/{id}/', expected_status=204)


    # ---------------------------------------------------------------------------
    # core.Token
    # ---------------------------------------------------------------------------


    async def token_add(self, data: JsonMapping | TokenRequest | None = None, **fields: Any) -> TokenDetail:
        return await self._request(
            'POST',
            'tokens/',
            json=self._serialize_body(data, **fields),
            response_model=TokenDetail,
        )


    # ---------------------------------------------------------------------------
    # core.AuditLog
    # ---------------------------------------------------------------------------


    async def auditlog_list(self, **params: Any) -> PaginatedAuditLogList:
        return await self._request(
            'GET', 'audit-logs/', params=params, response_model=PaginatedAuditLogList
        )

    async def auditlog_get(self, id: str) -> AuditLogDetail:
        return await self._request('GET', f'audit-logs/{id}/', response_model=AuditLogDetail)


    # ---------------------------------------------------------------------------
    # snapshots.Snapshot
    # ---------------------------------------------------------------------------


    async def snapshots_list(self, **params: Any) -> PaginatedSnapshotList:
        return await self._request(
            'GET', 'snapshots/', params=params, response_model=PaginatedSnapshotList
        )

    async def snapshots_get(self, id: str) -> SnapshotDetail:
        return await self._request('GET', f'snapshots/{id}/', response_model=SnapshotDetail)

    async def snapshots_update(
        self, id: str, data: JsonMapping | SnapshotUpdate | None = None, **fields: Any
    ) -> SnapshotDetail:
        return await self._request(
            'PATCH',
            f'snapshots/{id}/',
            json=self._serialize_body(data, **fields),
            response_model=SnapshotDetail,
        )

    async def snapshots_rm(self, id: str) -> None:
        return await self._request('DELETE', f'snapshots/{id}/', expected_status=204)

    async def snapshots_pin(
        self, id: str, data: JsonMapping | None = None, **fields: Any
    ) -> SnapshotDetail:
        return await self._request(
            'POST',
            f'snapshots/{id}/pin/',
            json=self._serialize_body(data, **fields),
            response_model=SnapshotDetail,
        )

    async def snapshots_unpin(
        self, id: str, data: JsonMapping | None = None, **fields: Any
    ) -> SnapshotDetail:
        return await self._request(
            'POST',
            f'snapshots/{id}/unpin/',
            json=self._serialize_body(data, **fields),
            response_model=SnapshotDetail,
        )

    async def snapshots_stats(self, id: str) -> SnapshotDetail:
        return await self._request('GET', f'snapshots/{id}/stats/', response_model=SnapshotDetail)

    async def snapshots_latest(self) -> SnapshotDetail:
        return await self._request('GET', 'snapshots/latest/', response_model=SnapshotDetail)
