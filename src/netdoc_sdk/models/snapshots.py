"""Pydantic models matching the public NetDoc OpenAPI snapshot contract."""

from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Any, List
from pydantic import Field
from netdoc_sdk.models.core import APIModel, LogMessage


class StatusEnum(str, Enum):
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    FAILED = 'failed'
    PARTIAL = 'partial'
    PENDING = 'pending'


class SnapshotDetail(APIModel):
    id: UUID
    label: str = ''
    description: str = ''
    pinned: bool = False
    status: StatusEnum
    log_messages: List[LogMessage]
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)
    completed_at: datetime | None = None
    created_at: datetime
    device_count: int = 0
    updated_at: datetime


class SnapshotList(APIModel):
    id: UUID
    label: str = ''
    pinned: bool = False
    status: StatusEnum
    # Metadata
    completed_at: datetime | None = None
    created_at: datetime
    device_count: int = 0
    updated_at: datetime


class SnapshotUpdate(APIModel):
    label: str | None = None
    description: str | None = None
    pinned: bool | None = None
    # Metadata
    metadata: dict[str, Any] | None = None
