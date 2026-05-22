from typing import Any, Generic, TypeVar
from netdoc_sdk.core.models import (
    JsonMapping,
    PaginatedAuditLogList,
    PaginatedTenantList,
    PaginatedUserList,
    AuditLogDetail,
    TenantCreate,
    TenantDetail,
    TenantUpdate,
    UserCreate,
    UserDetail,
    UserUpdate,
)


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
# core.AuditLog
# ---------------------------------------------------------------------------


async def auditlog_list(self, **params: Any) -> PaginatedAuditLogList:
    return await self._request(
        'GET', 'audit-logs/', params=params, response_model=PaginatedAuditLogList
    )

async def auditlog_get(self, id: str) -> AuditLogDetail:
    return await self._request('GET', f'audit-logs/{id}/', response_model=AuditLogDetail)
