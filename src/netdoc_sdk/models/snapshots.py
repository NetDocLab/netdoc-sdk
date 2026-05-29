"""Pydantic models matching the public NetDoc OpenAPI snapshot contracts."""

from datetime import datetime
from enum import Enum

from netdoc_sdk.models.core import APIModel, LogMessage, PaginatedResponse, UUID4Str


class StatusEnum(Enum):
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    FAILED = 'failed'
    PARTIAL = 'partial'
    PENDING = 'pending'


class SnapshotDetail(APIModel):
    id: UUID4Str
    label: str
    description: str
    status: StatusEnum
    pinned: bool
    log_messages: list[LogMessage]
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    device_count: int


class SnapshotList(APIModel):
    id: UUID4Str
    label: str
    status: StatusEnum
    pinned: bool
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    device_count: int


PaginatedSnapshotList = PaginatedResponse[SnapshotList]


class SnapshotUpdate(APIModel):
    label: str | None = None
    description: str | None = None
    pinned: bool | None = None
