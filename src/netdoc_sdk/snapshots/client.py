from typing import Any, Generic, TypeVar
from netdoc_sdk.core.models import JsonMapping
from netdoc_sdk.snapshots.models import (
    PaginatedSnapshotList,
    SnapshotDetail,
    SnapshotUpdate,
)


async def snapshots_list(self, **params: Any) -> PaginatedSnapshotList:
    return await self._request(
        'GET', 'snapshots/', params=params, response_model=PaginatedSnapshotList
    )

async def snapshots_get(self, id: str) -> SnapshotDetail:
    return await self._request('GET', f'snapshots/{id}/', response_model=SnapshotDetail)

async def snapshots_update(
    self, id: str, data: JsonMapping | SnapshotDetail | None = None, **fields: Any
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
