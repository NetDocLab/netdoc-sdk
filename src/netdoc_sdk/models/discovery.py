"""Pydantic models matching the public NetDoc OpenAPI discovery contracts."""

from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Any, List
from pydantic import Field
from netdoc_sdk.models.core import APIModel, PaginatedResponse, UUID4Str


# ---------------------------------------------------------------------------
# inventory.Collector
# ---------------------------------------------------------------------------


class CollectorDetail(APIModel):
    id: UUID4Str
    user: UUID
    name: str
    version: str
    canonical_devices: list[UUID] = Field(default_factory=list)
    sites: list[UUID] = Field(default_factory=list)
    domain_range: list[str] = Field(default_factory=list)
    network_range: list[str] = Field(default_factory=list)
    is_active: bool = True
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)
    last_heartbeat_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class CollectorList(APIModel):
    id: UUID4Str
    user: UUID
    name: str
    version: str
    is_active: bool = True
    # Metadata
    last_heartbeat_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


PaginatedCollectorList = PaginatedResponse[CollectorList]


class CollectorUpdate(APIModel):
    canonical_devices: list[UUID] = Field(default_factory=list)
    sites: list[UUID] = Field(default_factory=list)
    domain_range: list[str] = Field(default_factory=list)
    network_range: list[str] = Field(default_factory=list)
    is_active: bool = True
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)


class CollectorHeartbeat(APIModel):
    name: str = ''
    version: str = ''


# ---------------------------------------------------------------------------
# inventory.Credential
# ---------------------------------------------------------------------------


class CredentialDetail(APIModel):
    id: UUID4Str
    username: str = ''
    label: str
    description: str = ''
    verify_cert: bool = True
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class CredentialList(APIModel):
    id: UUID4Str
    username: str = ''
    label: str
    verify_cert: bool = True
    # Metadata
    created_at: datetime
    updated_at: datetime


PaginatedCredentialList = PaginatedResponse[CredentialList]


class CredentialCreate(APIModel):
    label: str
    description: str = ''
    username: str = ''
    verify_cert: bool = True
    password: str
    secret: str
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)


class CredentialUpdate(APIModel):
    label: str
    description: str = ''
    username: str = ''
    verify_cert: bool = True
    password: str
    secret: str
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# inventory.DiscoveryRun
# ---------------------------------------------------------------------------


# class DiscoveryRunCreate(APIModel):
#     collector_ids: list[str] = Field(default_factory=list)
#     command_profile: dict[str, Any] = Field(default_factory=dict)
#     parser_hints: dict[str, Any] = Field(default_factory=dict)
#     metadata: dict[str, Any] = Field(default_factory=dict)


# class DiscoveryRun(APIModel):
#     id: str
#     snapshot_id: str
#     status: DiscoveryRunStatusEnum | str = DiscoveryRunStatusEnum.PENDING
#     origin: str = 'manual'
#     requested_by: int | None = None
#     schedule: str | None = None
#     command_profile: dict[str, Any] = Field(default_factory=dict)
#     parser_hints: dict[str, Any] = Field(default_factory=dict)
#     metadata: dict[str, Any] = Field(default_factory=dict)
#     job_count: int = 0
#     completed_job_count: int = 0
#     failed_job_count: int = 0
#     raw_output_count: int = 0
#     error_message: str = ''
#     cancellation_requested_at: datetime | None = None
#     created_at: datetime
#     started_at: datetime | None = None
#     completed_at: datetime | None = None
#     updated_at: datetime | None = None


# class DiscoveryJob(APIModel):
#     id: str
#     run: str
#     collector: str
#     collector_name: str = ''
#     target_device: str | None = None
#     site: str | None = None
#     site_name: str | None = None
#     status: DiscoveryJobStatusEnum | str = DiscoveryJobStatusEnum.QUEUED
#     payload: dict[str, Any] = Field(default_factory=dict)
#     command_profile: dict[str, Any] = Field(default_factory=dict)
#     parser_hints: dict[str, Any] = Field(default_factory=dict)
#     claim_token: str | None = None
#     claimed_at: datetime | None = None
#     last_heartbeat_at: datetime | None = None
#     lease_expires_at: datetime | None = None
#     timeout_at: datetime | None = None
#     attempts: int = 0
#     max_attempts: int = 3
#     idempotency_key: str = ''
#     log_messages: list = []
#     created_at: datetime
#     updated_at: datetime | None = None


# class DiscoveryJobClaim(APIModel):
#     lease_seconds: int = 300


# class DiscoveryJobHeartbeat(APIModel):
#     claim_token: str


# class DiscoveryJobComplete(APIModel):
#     claim_token: str
#     status: DiscoveryJobStatusEnum | str
#     log_messages: list = []


# ---------------------------------------------------------------------------
# inventory.DiscoveryJob
# ---------------------------------------------------------------------------
