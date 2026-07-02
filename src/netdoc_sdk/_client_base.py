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
    ) -> None:
        self._client = None
        self.base_url = self._normalize_base_url(base_url)
        self.client_kwargs = dict(client_kwargs or {})
        self.cookies = dict(cookies or {})
        self.extra_headers = dict(headers or {})
        self.tenant_id = tenant_id
        self.max_retries = max_retries
        self.timeout = timeout
        self.token = token
        self.transport = transport

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

    # # ------------------------------------------------------------------
    # # Endpoint methods — return self._request(...) directly.
    # #
    # # Because ``_request`` is a coroutine in AsyncNetDocClient and a plain
    # # function in NetDocClient, these methods are naturally "transparent":
    # #   - sync callers get the result value immediately
    # #   - async callers get a coroutine they must ``await``
    # #
    # # No duplication needed; adding a new endpoint means one method here.
    # # ------------------------------------------------------------------

    # # core.Tenant

    # def tenant_add(
    #     self, data: JsonMapping | TenantCreate | None = None, **fields: Any
    # ) -> TenantDetail:
    #     """Create a new tenant."""
    #     return self._request(
    #         'POST',
    #         'tenants/',
    #         json=self._serialize_body(data, **fields),
    #         expected_status=201,
    #         response_model=TenantDetail,
    #     )

    # def tenant_list(self, **params: Any) -> PaginatedTenantList:
    #     """Return a paginated list of tenants."""
    #     return self._request(
    #         'GET',
    #         'tenants/',
    #         params=params,
    #         expected_status=200,
    #         response_model=PaginatedTenantList,
    #     )

    # def tenant_get(self, id: str) -> TenantDetail:
    #     """Retrieve a single tenant by ID."""
    #     return self._request(
    #         'GET',
    #         f'tenants/{id}/',
    #         expected_status=200,
    #         response_model=TenantDetail,
    #     )

    # def tenant_update(
    #     self, id: str, data: JsonMapping | TenantUpdate | None = None, **fields: Any
    # ) -> TenantDetail:
    #     """Partially update a tenant."""
    #     return self._request(
    #         'PATCH',
    #         f'tenants/{id}/',
    #         json=self._serialize_body(data, **fields),
    #         expected_status=200,
    #         response_model=TenantDetail,
    #     )

    # def tenant_delete(self, id: str) -> None:
    #     """Delete a tenant."""
    #     return self._request('DELETE', f'tenants/{id}/', expected_status=204)

    # def tenant_current(self) -> TenantDetail:
    #     """Return the tenant associated with the current token."""
    #     return self._request('GET', 'tenants/current/', response_model=TenantDetail)

    # # core.User

    # def user_add(self, data: JsonMapping | UserCreate | None = None, **fields: Any) -> UserDetail:
    #     """Create a new user."""
    #     return self._request(
    #         'POST',
    #         'users/',
    #         json=self._serialize_body(data, **fields),
    #         expected_status=201,
    #         response_model=UserDetail,
    #     )

    # def user_list(self, **params: Any) -> PaginatedUserList:
    #     """Return a paginated list of users."""
    #     return self._request(
    #         'GET',
    #         'users/',
    #         params=params,
    #         expected_status=200,
    #         response_model=PaginatedUserList,
    #     )

    # def user_get(self, id: str) -> UserDetail:
    #     """Retrieve a single user by ID."""
    #     return self._request(
    #         'GET',
    #         f'users/{id}/',
    #         expected_status=200,
    #         response_model=UserDetail,
    #     )

    # def user_update(
    #     self, id: str, data: JsonMapping | UserUpdate | None = None, **fields: Any
    # ) -> UserDetail:
    #     """Partially update a user."""
    #     return self._request(
    #         'PATCH',
    #         f'users/{id}/',
    #         json=self._serialize_body(data, **fields),
    #         expected_status=200,
    #         response_model=UserDetail,
    #     )

    # def user_delete(self, id: str) -> None:
    #     """Delete a user."""
    #     return self._request('DELETE', f'users/{id}/', expected_status=204)

    # def profile_get(self) -> UserDetail:
    #     """Return the profile of the currently authenticated user."""
    #     return self._request(
    #         'GET',
    #         'users/current/',
    #         expected_status=200,
    #         response_model=UserDetail,
    #     )

    # def profile_update(
    #     self, data: JsonMapping | UserProfileUpdate | None = None, **fields: Any
    # ) -> UserDetail:
    #     """Update the profile of the currently authenticated user."""
    #     return self._request(
    #         'PATCH',
    #         'users/current/',
    #         json=self._serialize_body(data, **fields),
    #         expected_status=200,
    #         response_model=UserDetail,
    #     )

    # # core.Token

    # def token_add(
    #     self, data: JsonMapping | TokenRequest | None = None, **fields: Any
    # ) -> TokenDetail:
    #     """Obtain an API token from username and password credentials."""
    #     return self._request(
    #         'POST',
    #         'tokens/',
    #         json=self._serialize_body(data, **fields),
    #         expected_status=200,
    #         response_model=TokenDetail,
    #     )

    # # core.AuditLog

    # def auditlog_list(self, **params: Any) -> PaginatedAuditLogList:
    #     """Return a paginated list of audit log entries."""
    #     return self._request(
    #         'GET',
    #         'audit-logs/',
    #         params=params,
    #         expected_status=200,
    #         response_model=PaginatedAuditLogList,
    #     )

    # def auditlog_get(self, id: str) -> AuditLogDetail:
    #     """Retrieve a single audit log entry by ID."""
    #     return self._request(
    #         'GET',
    #         f'audit-logs/{id}/',
    #         expected_status=200,
    #         response_model=AuditLogDetail,
    #     )

    # # core.LogRecord

    # def log_add(self, data: JsonMapping | LogCreate | None = None, **fields: Any) -> LogDetail:
    #     """Create a log record."""
    #     return self._request(
    #         'POST',
    #         'logs/',
    #         json=self._serialize_body(data, **fields),
    #         expected_status=201,
    #         response_model=LogDetail,
    #     )

    # def log_list(self, **params: Any) -> PaginatedLogList:
    #     """Return a paginated list of log records."""
    #     return self._request(
    #         'GET',
    #         'logs/',
    #         params=params,
    #         expected_status=200,
    #         response_model=PaginatedLogList,
    #     )

    # def log_get(self, id: str) -> LogDetail:
    #     """Retrieve a single log record by ID."""
    #     return self._request(
    #         'GET',
    #         f'logs/{id}/',
    #         expected_status=200,
    #         response_model=LogDetail,
    #     )

    # # snapshots.Snapshot

    # def snapshot_list(self, **params: Any) -> PaginatedSnapshotList:
    #     """Return a paginated list of snapshots."""
    #     return self._request(
    #         'GET',
    #         'snapshots/',
    #         params=params,
    #         expected_status=200,
    #         response_model=PaginatedSnapshotList,
    #     )

    # def snapshot_get(self, id: str) -> SnapshotDetail:
    #     """Retrieve a single snapshot by ID."""
    #     return self._request(
    #         'GET',
    #         f'snapshots/{id}/',
    #         expected_status=200,
    #         response_model=SnapshotDetail,
    #     )

    # def snapshot_update(
    #     self, id: str, data: JsonMapping | SnapshotUpdate | None = None, **fields: Any
    # ) -> SnapshotDetail:
    #     """Partially update a snapshot."""
    #     return self._request(
    #         'PATCH',
    #         f'snapshots/{id}/',
    #         json=self._serialize_body(data, **fields),
    #         expected_status=200,
    #         response_model=SnapshotDetail,
    #     )

    # def snapshot_delete(self, id: str) -> None:
    #     """Delete a snapshot."""
    #     return self._request('DELETE', f'snapshots/{id}/', expected_status=204)

    # def snapshot_pin(
    #     self, id: str, data: JsonMapping | None = None, **fields: Any
    # ) -> SnapshotDetail:
    #     """Pin a snapshot so it is excluded from automatic pruning."""
    #     return self._request(
    #         'POST',
    #         f'snapshots/{id}/pin/',
    #         json=self._serialize_body(data, **fields),
    #         expected_status=200,
    #         response_model=SnapshotDetail,
    #     )

    # def snapshot_unpin(
    #     self, id: str, data: JsonMapping | None = None, **fields: Any
    # ) -> SnapshotDetail:
    #     """Remove the pin from a snapshot."""
    #     return self._request(
    #         'POST',
    #         f'snapshots/{id}/unpin/',
    #         json=self._serialize_body(data, **fields),
    #         expected_status=200,
    #         response_model=SnapshotDetail,
    #     )

    # def snapshot_stats(self, id: str) -> SnapshotDetail:
    #     """Return statistics for a snapshot."""
    #     return self._request(
    #         'GET',
    #         f'snapshots/{id}/stats/',
    #         expected_status=200,
    #         response_model=SnapshotDetail,
    #     )

    # def snapshot_latest(self) -> SnapshotDetail:
    #     """Return the most recent snapshot."""
    #     return self._request(
    #         'GET',
    #         'snapshots/latest/',
    #         expected_status=200,
    #         response_model=SnapshotDetail,
    #     )

    # # discovery.DiscoveryRun

    # def discovery_add(self) -> DiscoveryRunDetail:
    #     """Trigger a new discovery run."""
    #     return self._request(
    #         'POST',
    #         'discoveries/',
    #         expected_status=201,
    #         response_model=DiscoveryRunDetail,
    #     )

    # def discovery_list(self, **params: Any) -> PaginatedDiscoveryRunList:
    #     """Return a paginated list of discovery runs."""
    #     return self._request(
    #         'GET',
    #         'discoveries/',
    #         params=params,
    #         expected_status=200,
    #         response_model=PaginatedDiscoveryRunList,
    #     )

    # def discovery_get(self, id: str) -> DiscoveryRunDetail:
    #     """Retrieve a single discovery run by ID."""
    #     return self._request(
    #         'GET',
    #         f'discoveries/{id}/',
    #         expected_status=200,
    #         response_model=DiscoveryRunDetail,
    #     )

    # def discovery_cancel(self, id: str) -> None:
    #     """Cancel a running discovery run."""
    #     return self._request(
    #         'POST',
    #         f'discoveries/{id}/cancel/',
    #         expected_status=204,
    #     )

    # def discovery_jobs(self, id: str) -> PaginatedDiscoveryJobList:
    #     """Return the jobs belonging to a discovery run."""
    #     return self._request(
    #         'GET',
    #         f'discoveries/{id}/jobs/',
    #         expected_status=200,
    #         response_model=PaginatedDiscoveryJobList,
    #     )

    # # discovery.DiscoveryJob

    # def discoveryjob_claim(self) -> DiscoveryJobClaim:
    #     """Claim the next available discovery job for processing."""
    #     return self._request(
    #         'POST',
    #         'discovery-jobs/claim/',
    #         expected_status=[200, 204],
    #         response_model=DiscoveryJobClaim,
    #     )

    # def discoveryjob_complete(
    #     self,
    #     id: str,
    #     claim_token: str,
    #     data: JsonMapping | CollectorJobCompleted | None = None,
    #     **fields: Any,
    # ) -> DiscoveryJobDetail:
    #     """Mark a discovery job as completed and submit its results."""
    #     return self._request(
    #         'POST',
    #         f'discovery-jobs/{id}/complete/',
    #         json=self._serialize_body(data, **fields),
    #         headers={'X-Claim-Token': claim_token},
    #         expected_status=204,
    #     )

    # def discoveryjob_push_discovered_device(
    #     self,
    #     id: str,
    #     claim_token: str,
    #     data: JsonMapping | DiscoveryJobPush | None = None,
    #     **fields: Any,
    # ) -> DiscoveryJobDetail:
    #     """Push a single discovered device to the backend during job execution."""
    #     return self._request(
    #         'POST',
    #         f'discovery-jobs/{id}/push-discovered-device/',
    #         json=self._serialize_body(data, **fields),
    #         headers={'X-Claim-Token': claim_token},
    #         expected_status=200,
    #         response_model=DiscoveryJobPush,
    #     )

    # def discoveryjob_logs(self, id: str) -> PaginatedRawOutputList:
    #     """Return the raw output logs for a discovery job."""
    #     return self._request(
    #         'GET',
    #         f'discovery-jobs/{id}/logs/',
    #         expected_status=200,
    #         response_model=PaginatedRawOutputList,
    #     )

    # # discovery.Collector

    # def collector_list(self, **params: Any) -> PaginatedCollectorList:
    #     """Return a paginated list of collectors."""
    #     return self._request(
    #         'GET',
    #         'collectors/',
    #         params=params,
    #         expected_status=200,
    #         response_model=PaginatedCollectorList,
    #     )

    # def collector_get(self, id: str) -> CollectorDetail:
    #     """Retrieve a single collector by ID."""
    #     return self._request(
    #         'GET',
    #         f'collectors/{id}/',
    #         expected_status=200,
    #         response_model=CollectorDetail,
    #     )

    # def collector_update(
    #     self, id: str, data: JsonMapping | CollectorUpdate | None = None, **fields: Any
    # ) -> CollectorDetail:
    #     """Partially update a collector's configuration."""
    #     return self._request(
    #         'PATCH',
    #         f'collectors/{id}/',
    #         json=self._serialize_body(data, **fields),
    #         expected_status=200,
    #         response_model=CollectorDetail,
    #     )

    # def collector_delete(self, id: str) -> None:
    #     """Delete a collector registration."""
    #     return self._request('DELETE', f'collectors/{id}/', expected_status=204)

    # def collector_heartbeat(
    #     self, data: JsonMapping | CollectorHeartbeat | None = None, **fields: Any
    # ) -> None:
    #     """Send a heartbeat to keep the collector registration alive."""
    #     return self._request(
    #         'POST',
    #         'collectors/heartbeat/',
    #         json=self._serialize_body(data, **fields),
    #         expected_status=200,
    #         response_model=CollectorDetail,
    #     )

    # # discovery.Credential

    # def credential_add(
    #     self, data: JsonMapping | CredentialCreate | None = None, **fields: Any
    # ) -> CredentialDetail:
    #     """Create a new device credential."""
    #     return self._request(
    #         'POST',
    #         'credentials/',
    #         json=self._serialize_body(data, **fields),
    #         expected_status=201,
    #         response_model=CredentialDetail,
    #     )

    # def credential_list(self, **params: Any) -> PaginatedCredentialList:
    #     """Return a paginated list of credentials."""
    #     return self._request(
    #         'GET',
    #         'credentials/',
    #         params=params,
    #         expected_status=200,
    #         response_model=PaginatedCredentialList,
    #     )

    # def credential_get(self, id: str) -> CredentialDetail:
    #     """Retrieve a single credential by ID."""
    #     return self._request(
    #         'GET',
    #         f'credentials/{id}/',
    #         expected_status=200,
    #         response_model=CredentialDetail,
    #     )

    # def credential_update(
    #     self, id: str, data: JsonMapping | CredentialUpdate | None = None, **fields: Any
    # ) -> CredentialDetail:
    #     """Partially update a credential."""
    #     return self._request(
    #         'PATCH',
    #         f'credentials/{id}/',
    #         json=self._serialize_body(data, **fields),
    #         expected_status=200,
    #         response_model=CredentialDetail,
    #     )

    # def credential_delete(self, id: str) -> None:
    #     """Delete a credential."""
    #     return self._request('DELETE', f'credentials/{id}/', expected_status=204)

    # # inventory.CanonicalDevice

    # def canonicaldevice_add(
    #     self, data: JsonMapping | CanonicalDeviceCreate | None = None, **fields: Any
    # ) -> CanonicalDeviceDetail:
    #     """Create a new canonical device."""
    #     return self._request(
    #         'POST',
    #         'canonical-devices/',
    #         json=self._serialize_body(data, **fields),
    #         expected_status=201,
    #         response_model=CanonicalDeviceDetail,
    #     )

    # def canonicaldevice_list(self, **params: Any) -> PaginatedCanonicalDeviceList:
    #     """Return a paginated list of canonical devices."""
    #     return self._request(
    #         'GET',
    #         'canonical-devices/',
    #         params=params,
    #         expected_status=200,
    #         response_model=PaginatedCanonicalDeviceList,
    #     )

    # def canonicaldevice_get(self, id: str) -> CanonicalDeviceDetail:
    #     """Retrieve a single canonical device by ID."""
    #     return self._request(
    #         'GET',
    #         f'canonical-devices/{id}/',
    #         expected_status=200,
    #         response_model=CanonicalDeviceDetail,
    #     )

    # def canonicaldevice_update(
    #     self, id: str, data: JsonMapping | CanonicalDeviceUpdate | None = None, **fields: Any
    # ) -> CanonicalDeviceDetail:
    #     """Partially update a canonical device."""
    #     return self._request(
    #         'PATCH',
    #         f'canonical-devices/{id}/',
    #         json=self._serialize_body(data, **fields),
    #         expected_status=200,
    #         response_model=CanonicalDeviceDetail,
    #     )

    # def canonicaldevice_delete(self, id: str) -> None:
    #     """Delete a canonical device."""
    #     return self._request('DELETE', f'canonical-devices/{id}/', expected_status=204)

    # # inventory.Site

    # def site_add(self, data: JsonMapping | SiteCreate | None = None, **fields: Any) -> SiteDetail:
    #     """Create a new site."""
    #     return self._request(
    #         'POST',
    #         'sites/',
    #         json=self._serialize_body(data, **fields),
    #         expected_status=201,
    #         response_model=SiteDetail,
    #     )

    # def site_list(self, **params: Any) -> PaginatedSiteList:
    #     """Return a paginated list of sites."""
    #     return self._request(
    #         'GET',
    #         'sites/',
    #         params=params,
    #         expected_status=200,
    #         response_model=PaginatedSiteList,
    #     )

    # def site_get(self, id: str) -> SiteDetail:
    #     """Retrieve a single site by ID."""
    #     return self._request(
    #         'GET',
    #         f'sites/{id}/',
    #         expected_status=200,
    #         response_model=SiteDetail,
    #     )

    # def site_update(
    #     self, id: str, data: JsonMapping | SiteUpdate | None = None, **fields: Any
    # ) -> SiteDetail:
    #     """Partially update a site."""
    #     return self._request(
    #         'PATCH',
    #         f'sites/{id}/',
    #         json=self._serialize_body(data, **fields),
    #         expected_status=200,
    #         response_model=SiteDetail,
    #     )

    # def site_delete(self, id: str) -> None:
    #     """Delete a site."""
    #     return self._request('DELETE', f'sites/{id}/', expected_status=204)
