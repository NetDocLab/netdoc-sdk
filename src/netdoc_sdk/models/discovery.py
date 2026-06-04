"""Pydantic models matching the public NetDoc OpenAPI discovery contracts."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from netdoc_sdk.models.core import APIModel, LogMessage, PaginatedResponse, UUID4Str

# ---------------------------------------------------------------------------
# inventory.Collector
# ---------------------------------------------------------------------------


class CollectorDetail(APIModel):
    id: UUID4Str
    user: UUID
    name: str
    version: str
    is_active: bool
    canonical_devices: list[UUID]
    sites: list[UUID]
    domain_ranges: list[str]
    network_ranges: list[str]
    created_at: datetime
    updated_at: datetime
    last_heartbeat_at: datetime | None


class CollectorList(APIModel):
    id: UUID4Str
    user: UUID
    name: str
    version: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_heartbeat_at: datetime | None


PaginatedCollectorList = PaginatedResponse[CollectorList]


class CollectorUpdate(APIModel):
    canonical_devices: list[UUID] | None = None
    sites: list[UUID] | None = None
    domain_range: list[str] | None = None
    network_range: list[str] | None = None
    is_active: bool | None = None


class CollectorHeartbeat(APIModel):
    name: str
    version: str


# ---------------------------------------------------------------------------
# inventory.Credential
# ---------------------------------------------------------------------------


class CredentialDetail(APIModel):
    id: UUID4Str
    label: str | None
    username: str | None
    description: str
    verify_cert: bool
    created_at: datetime
    updated_at: datetime


class CredentialList(APIModel):
    id: UUID4Str
    username: str | None
    label: str
    verify_cert: bool
    created_at: datetime
    updated_at: datetime


PaginatedCredentialList = PaginatedResponse[CredentialList]


class CredentialCreate(APIModel):
    label: str
    description: str | None = None
    username: str | None = None
    password: str | None = None
    secret: str | None = None
    verify_cert: bool | None = None


class CredentialUpdate(APIModel):
    label: str | None = None
    description: str | None = None
    username: str | None = None
    password: str | None = None
    secret: str | None = None
    verify_cert: bool | None = None


# ---------------------------------------------------------------------------
# inventory.DiscoveryRun
# ---------------------------------------------------------------------------


class DiscoveryRunStatusEnum(Enum):
    CANCELLED = 'cancelled'
    CANCELLING = 'cancelling'
    COMPLETED = 'completed'
    FAILED = 'failed'
    PENDING = 'pending'
    RUNNING = 'running'


class DiscoveryRunDetail(APIModel):
    id: str
    snapshot_id: str
    status: DiscoveryRunStatusEnum
    origin: str
    requested_by: UUID4Str | None
    schedule: UUID4Str | None
    log_messages: list[LogMessage]
    completed_job_count: int
    failed_job_count: int
    job_count: int
    raw_output_count: int
    parsed_output_count: int
    cancellation_requested_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    started_at: datetime | None
    updated_at: datetime


class DiscoveryRunList(APIModel):
    id: str
    snapshot_id: str
    status: DiscoveryRunStatusEnum
    origin: str
    requested_by: UUID4Str | None
    schedule: UUID4Str | None
    completed_job_count: int
    failed_job_count: int
    job_count: int
    raw_output_count: int
    parsed_output_count: int
    cancellation_requested_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    started_at: datetime | None
    updated_at: datetime


PaginatedDiscoveryRunList = PaginatedResponse[DiscoveryRunList]


# ---------------------------------------------------------------------------
# inventory.DiscoveryJob
# ---------------------------------------------------------------------------

# claim
# heartbeat
# push_discovered_device
# status
# complete


class DiscoveryJobDetail(APIModel):
    id: str
    run: UUID4Str
    collector: UUID4Str
    collector_name: str
    snapshot: UUID4Str
    status: str
    attempt: int
    max_attempts: int
    idempotency_key: str
    log_messages: list[LogMessage]
    claimed_at: datetime | None
    last_heartbeat_at: datetime | None
    lease_expires_at: datetime | None
    timeout_at: datetime | None
    created_at: datetime
    updated_at: datetime


PaginatedDiscoveryJobList = PaginatedResponse[DiscoveryJobDetail]


class DiscoveryJobClaim(APIModel):
    id: str
    run: UUID4Str
    collector: UUID4Str
    collector_name: str
    snapshot: UUID4Str
    status: str
    attempt: int
    max_attempts: int
    idempotency_key: str
    log_messages: list[LogMessage]
    inventory: dict
    claimed_at: datetime | None
    last_heartbeat_at: datetime | None
    lease_expires_at: datetime | None
    timeout_at: datetime | None
    created_at: datetime
    updated_at: datetime


# class DiscoveryJobHeartbeat(APIModel):
#     claim_token: str


# class DiscoveryJobComplete(APIModel):
#     claim_token: str
#     status: DiscoveryJobStatusEnum | str
#     log_messages: list = []
