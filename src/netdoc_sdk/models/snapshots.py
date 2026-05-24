"""Pydantic models matching the public NetDoc OpenAPI snapshot contracts."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field

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
    pinned: bool
    status: StatusEnum
    log_messages: list[LogMessage]
    # Metadata
    metadata: dict[str, Any]
    completed_at: datetime | None
    created_at: datetime
    device_count: int
    updated_at: datetime


class SnapshotList(APIModel):
    id: UUID4Str
    label: str
    pinned: bool
    status: StatusEnum
    # Metadata
    completed_at: datetime | None
    created_at: datetime
    device_count: int
    updated_at: datetime


PaginatedSnapshotList = PaginatedResponse[SnapshotList]


class SnapshotUpdate(APIModel):
    label: str | None = None
    description: str | None = None
    pinned: bool | None = None
    # Metadata
    metadata: dict[str, Any] | None = None
