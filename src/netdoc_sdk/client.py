"""Async HTTP client for the NetDoc OpenAPI surface."""

import asyncio
import logging
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
    UserProfileUpdate,
    UserUpdate,
)
from netdoc_sdk.models.discovery import (
    CollectorDetail,
    CollectorHeartbeat,
    CollectorJobCompleted,
    CollectorUpdate,
    CredentialCreate,
    CredentialDetail,
    CredentialUpdate,
    DiscoveredDeviceSubmit,
    DiscoveryJobClaim,
    DiscoveryJobDetail,
    DiscoveryJobStatusEnum,
    DiscoveryRunDetail,
    PaginatedCollectorList,
    PaginatedCredentialList,
    PaginatedDiscoveryJobList,
    PaginatedDiscoveryRunList,
)
from netdoc_sdk.models.inventory import (
    CanonicalDeviceCreate,
    CanonicalDeviceDetail,
    CanonicalDeviceUpdate,
    PaginatedCanonicalDeviceList,
    PaginatedSiteList,
    SiteCreate,
    SiteDetail,
    SiteUpdate,
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
        max_retries: int = 5,
        timeout: float = 30.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        self._client: httpx.AsyncClient | None = None
        self.base_url = self._normalize_base_url(base_url)
        self.client_kwargs = dict(client_kwargs or {})
        self.cookies = dict(cookies or {})
        self.extra_headers = dict(headers or {})
        self.tenant_id = tenant_id
        self.max_retries = max_retries
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
            token = await bootstrap.token_add(username=username, password=password)
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
        request_headers = {}
        if method.upper() in ('POST', 'PUT', 'PATCH'):
            request_headers['Content-Type'] = 'application/json'
        if headers:
            request_headers.update(headers)

        expected = None
        if expected_status is not None:
            expected = (
                {expected_status} if isinstance(expected_status, int) else set(expected_status)
            )

        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.request(
                    content=content,
                    headers=request_headers,
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

            if ok:
                break

            if response.status_code == 429 and attempt < self.max_retries:
                # Retry with rate limit
                default_retry_after = '1.0'
                retry_after = response.headers.get('Retry-After')
                if not retry_after:
                    logging.warning(f'Retry value not set, using {default_retry_after}')
                    retry_after = default_retry_after
                try:
                    wait = float(retry_after)
                except (ValueError, TypeError):
                    logging.warning(
                        f'Retry value of {retry_after} is not valid, using {default_retry_after}'
                    )
                    wait = float(default_retry_after)
                logging.warning(
                    'Rate limited (attempt %d/%d), retrying in %.1fs',
                    attempt + 1,
                    self.max_retries,
                    wait,
                )
                await asyncio.sleep(wait)
                continue

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

    async def tenant_update(
        self, id: str, data: JsonMapping | TenantUpdate | None = None, **fields: Any
    ) -> TenantDetail:
        return await self._request(
            'PATCH',
            f'tenants/{id}/',
            json=self._serialize_body(data, **fields),
            response_model=TenantDetail,
        )

    async def tenant_delete(self, id: str) -> None:
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
        return await self._request('GET', 'users/', params=params, response_model=PaginatedUserList)

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

    async def user_delete(self, id: str) -> None:
        return await self._request('DELETE', f'users/{id}/', expected_status=204)

    async def profile_get(self) -> UserDetail:
        return await self._request('GET', 'users/current/', response_model=UserDetail)

    async def profile_update(
        self, data: JsonMapping | UserProfileUpdate | None = None, **fields: Any
    ) -> UserDetail:
        return await self._request(
            'PATCH',
            'users/current/',
            json=self._serialize_body(data, **fields),
            response_model=UserDetail,
        )

    # ---------------------------------------------------------------------------
    # core.Token
    # ---------------------------------------------------------------------------

    async def token_add(
        self, data: JsonMapping | TokenRequest | None = None, **fields: Any
    ) -> TokenDetail:
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

    async def snapshot_list(self, **params: Any) -> PaginatedSnapshotList:
        return await self._request(
            'GET', 'snapshots/', params=params, response_model=PaginatedSnapshotList
        )

    async def snapshot_get(self, id: str) -> SnapshotDetail:
        return await self._request('GET', f'snapshots/{id}/', response_model=SnapshotDetail)

    async def snapshot_update(
        self, id: str, data: JsonMapping | SnapshotUpdate | None = None, **fields: Any
    ) -> SnapshotDetail:
        return await self._request(
            'PATCH',
            f'snapshots/{id}/',
            json=self._serialize_body(data, **fields),
            response_model=SnapshotDetail,
        )

    async def snapshot_delete(self, id: str) -> None:
        return await self._request('DELETE', f'snapshots/{id}/', expected_status=204)

    async def snapshot_pin(
        self, id: str, data: JsonMapping | None = None, **fields: Any
    ) -> SnapshotDetail:
        return await self._request(
            'POST',
            f'snapshots/{id}/pin/',
            json=self._serialize_body(data, **fields),
            response_model=SnapshotDetail,
        )

    async def snapshot_unpin(
        self, id: str, data: JsonMapping | None = None, **fields: Any
    ) -> SnapshotDetail:
        return await self._request(
            'POST',
            f'snapshots/{id}/unpin/',
            json=self._serialize_body(data, **fields),
            response_model=SnapshotDetail,
        )

    async def snapshot_stats(self, id: str) -> SnapshotDetail:
        return await self._request('GET', f'snapshots/{id}/stats/', response_model=SnapshotDetail)

    async def snapshot_latest(self) -> SnapshotDetail:
        return await self._request('GET', 'snapshots/latest/', response_model=SnapshotDetail)

    # ---------------------------------------------------------------------------
    # discovery.DiscoveryRun
    # ---------------------------------------------------------------------------

    async def discovery_add(self) -> DiscoveryRunDetail:
        return await self._request(
            'POST',
            'discoveries/',
            expected_status=201,
            response_model=DiscoveryRunDetail,
        )

    async def discovery_list(self, **params: Any) -> PaginatedDiscoveryRunList:
        return await self._request(
            'GET', 'discoveries/', params=params, response_model=PaginatedDiscoveryRunList
        )

    async def discovery_get(self, id: str) -> DiscoveryRunDetail:
        return await self._request('GET', f'discoveries/{id}/', response_model=DiscoveryRunDetail)

    async def discovery_cancel(self, id: str) -> DiscoveryRunDetail:
        return await self._request(
            'POST', f'discoveries/{id}/cancel/', response_model=DiscoveryRunDetail
        )

    async def discovery_jobs(self, id: str) -> PaginatedDiscoveryJobList:
        return await self._request(
            'GET', f'discoveries/{id}/jobs/', response_model=PaginatedDiscoveryJobList
        )

    # ---------------------------------------------------------------------------
    # discovery.DiscoveryJob
    # ---------------------------------------------------------------------------

    async def discoveryjob_claim(self) -> DiscoveryJobClaim:
        return await self._request(
            'POST', 'discovery-jobs/claim/', response_model=DiscoveryJobClaim
        )

    async def discoveryjob_complete(
        self,
        id: str,
        claim_token: str,
        data: JsonMapping | CollectorJobCompleted | None = None,
        **fields: Any,
    ) -> DiscoveryJobDetail:
        # TODO: could be no content
        headers = {'X-Claim-Token': claim_token}
        return await self._request(
            'POST',
            f'discovery-jobs/{id}/complete/',
            json=self._serialize_body(data, **fields),
            headers=headers,
            response_model=DiscoveryJobDetail,
        )

    async def discoveryjob_heartbeat(self, id: str, claim_token: str) -> DiscoveryJobDetail:
        # TODO: could be no content
        headers = {'X-Claim-Token': claim_token}
        return await self._request(
            'POST',
            f'discovery-jobs/{id}/heartbeat/',
            headers=headers,
            response_model=DiscoveryJobDetail,
        )

    async def discoveryjob_push_discovered_device(
        self,
        id: str,
        claim_token: str,
        data: JsonMapping | DiscoveredDeviceSubmit | None = None,
        **fields: Any,
    ) -> DiscoveryJobDetail:
        # TODO: could be no content
        headers = {'X-Claim-Token': claim_token}
        return await self._request(
            'POST',
            f'discovery-jobs/{id}/push-discovered-device/',
            json=self._serialize_body(data, **fields),
            headers=headers,
            response_model=DiscoveryJobDetail,
        )

    async def discoveryjob_status(
        self, id: str, claim_token: str, status: DiscoveryJobStatusEnum | None = None
    ) -> DiscoveryJobDetail:
        headers = {'X-Claim-Token': claim_token}
        if status is not None:
            return await self._request(
                'PATCH',
                f'discovery-jobs/{id}/status/',
                headers=headers,
                json={'status': status},
                response_model=DiscoveryJobDetail,
            )
        return await self._request(
            'GET',
            f'discovery-jobs/{id}/status/',
            headers=headers,
            response_model=DiscoveryJobDetail,
        )

    # TODO
    # push_discovered_device
    # status --> implement both GET and PATCH to update the status (e.g. to mark complete or failed)
    # complete

    # ---------------------------------------------------------------------------
    # discovery.Collector
    # ---------------------------------------------------------------------------

    async def collector_list(self, **params: Any) -> PaginatedCollectorList:
        return await self._request(
            'GET', 'collectors/', params=params, response_model=PaginatedCollectorList
        )

    async def collector_get(self, id: str) -> CollectorDetail:
        return await self._request('GET', f'collectors/{id}/', response_model=CollectorDetail)

    async def collector_update(
        self, id: str, data: JsonMapping | CollectorUpdate | None = None, **fields: Any
    ) -> CollectorDetail:
        return await self._request(
            'PATCH',
            f'collectors/{id}/',
            json=self._serialize_body(data, **fields),
            response_model=CollectorDetail,
        )

    async def collector_delete(self, id: str) -> None:
        return await self._request('DELETE', f'collectors/{id}/', expected_status=204)

    async def collector_heartbeat(
        self, data: JsonMapping | CollectorHeartbeat | None = None, **fields: Any
    ) -> None:
        return await self._request(
            'POST',
            'collectors/heartbeat/',
            json=self._serialize_body(data, **fields),
            expected_status=200,
            response_model=CollectorDetail,
        )

    # ---------------------------------------------------------------------------
    # discovery.Credential
    # ---------------------------------------------------------------------------

    async def credential_add(
        self, data: JsonMapping | CredentialCreate | None = None, **fields: Any
    ) -> CredentialDetail:
        return await self._request(
            'POST',
            'credentials/',
            json=self._serialize_body(data, **fields),
            expected_status=201,
            response_model=CredentialDetail,
        )

    async def credential_list(self, **params: Any) -> PaginatedCredentialList:
        return await self._request(
            'GET', 'credentials/', params=params, response_model=PaginatedCredentialList
        )

    async def credential_get(self, id: str) -> CredentialDetail:
        return await self._request('GET', f'credentials/{id}/', response_model=CredentialDetail)

    async def credential_update(
        self, id: str, data: JsonMapping | CredentialUpdate | None = None, **fields: Any
    ) -> CredentialDetail:
        return await self._request(
            'PATCH',
            f'credentials/{id}/',
            json=self._serialize_body(data, **fields),
            response_model=CredentialDetail,
        )

    async def credential_delete(self, id: str) -> None:
        return await self._request('DELETE', f'credentials/{id}/', expected_status=204)

    # ---------------------------------------------------------------------------
    # inventory.CanonicalDevice
    # ---------------------------------------------------------------------------

    async def canonicaldevice_add(
        self, data: JsonMapping | CanonicalDeviceCreate | None = None, **fields: Any
    ) -> CanonicalDeviceDetail:
        return await self._request(
            'POST',
            'canonical-devices/',
            json=self._serialize_body(data, **fields),
            expected_status=201,
            response_model=CanonicalDeviceDetail,
        )

    async def canonicaldevice_list(self, **params: Any) -> PaginatedCanonicalDeviceList:
        return await self._request(
            'GET', 'canonical-devices/', params=params, response_model=PaginatedCanonicalDeviceList
        )

    async def canonicaldevice_get(self, id: str) -> CanonicalDeviceDetail:
        return await self._request(
            'GET', f'canonical-devices/{id}/', response_model=CanonicalDeviceDetail
        )

    async def canonicaldevice_update(
        self, id: str, data: JsonMapping | CanonicalDeviceUpdate | None = None, **fields: Any
    ) -> CanonicalDeviceDetail:
        return await self._request(
            'PATCH',
            f'canonical-devices/{id}/',
            json=self._serialize_body(data, **fields),
            response_model=CanonicalDeviceDetail,
        )

    async def canonicaldevice_delete(self, id: str) -> None:
        return await self._request('DELETE', f'canonical-devices/{id}/', expected_status=204)

    # async def canonicaldevice_history(self, id: str) -> PaginatedDeviceList:
    # TODO
    # return await self._request('GET', f'canonical-devices/{id}/history/', response_model=PaginatedDeviceList)

    # ---------------------------------------------------------------------------
    # inventory.Site
    # ---------------------------------------------------------------------------

    async def site_add(
        self, data: JsonMapping | SiteCreate | None = None, **fields: Any
    ) -> SiteDetail:
        return await self._request(
            'POST',
            'sites/',
            json=self._serialize_body(data, **fields),
            expected_status=201,
            response_model=SiteDetail,
        )

    async def site_list(self, **params: Any) -> PaginatedSiteList:
        return await self._request('GET', 'sites/', params=params, response_model=PaginatedSiteList)

    async def site_get(self, id: str) -> SiteDetail:
        return await self._request('GET', f'sites/{id}/', response_model=SiteDetail)

    async def site_update(
        self, id: str, data: JsonMapping | SiteUpdate | None = None, **fields: Any
    ) -> SiteDetail:
        return await self._request(
            'PATCH',
            f'sites/{id}/',
            json=self._serialize_body(data, **fields),
            response_model=SiteDetail,
        )

    async def site_delete(self, id: str) -> None:
        return await self._request('DELETE', f'sites/{id}/', expected_status=204)
