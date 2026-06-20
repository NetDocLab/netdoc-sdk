"""Pydantic models matching the public NetDoc OpenAPI discovery contracts."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, field_validator

from netdoc_sdk.models.core import APIModel, LogMessage, PaginatedResponse, UUID4Str

# ---------------------------------------------------------------------------
# discovery.Collector
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


PaginatedCollectorList = PaginatedResponse[CollectorDetail]


class CollectorUpdate(APIModel):
    canonical_devices: list[UUID] | None = None
    sites: list[UUID] | None = None
    domain_range: list[str] | None = None
    network_range: list[str] | None = None
    is_active: bool | None = None


class CollectorHeartbeat(APIModel):
    name: str
    version: str


class CollectorJobStatusEnum(Enum):
    """Collector job lifecycle statuses."""

    QUEUED = 'queued'
    CLAIMED = 'claimed'
    RUNNING = 'running'
    CANCELLING = 'cancelling'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    FAILED = 'failed'
    EXPIRED = 'expired'


class CollectorJobCompleted(APIModel):
    status: CollectorJobStatusEnum
    log_messages: list | None = None


# ---------------------------------------------------------------------------
# discovery.Credential
# ---------------------------------------------------------------------------


class CredentialDetail(APIModel):
    id: UUID4Str
    label: str | None
    username: str | None
    description: str
    verify_cert: bool
    created_at: datetime
    updated_at: datetime


PaginatedCredentialList = PaginatedResponse[CredentialDetail]


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
# discovery.DiscoveryRun
# ---------------------------------------------------------------------------


class DiscoveryRunStatusEnum(Enum):
    CANCELLED = 'cancelled'
    CANCELLING = 'cancelling'
    COMPLETED = 'completed'
    FAILED = 'failed'
    PENDING = 'pending'
    RUNNING = 'running'


class DiscoveryRunDetail(APIModel):
    id: UUID4Str
    snapshot: UUID4Str
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


PaginatedDiscoveryRunList = PaginatedResponse[DiscoveryRunDetail]


# ---------------------------------------------------------------------------
# discovery.DiscoveryJob
# ---------------------------------------------------------------------------


class DiscoveryJobStatusEnum(Enum):
    """Discovery job lifecycle statuses."""

    QUEUED = 'queued'
    CLAIMED = 'claimed'
    RUNNING = 'running'
    CANCELLING = 'cancelling'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    FAILED = 'failed'
    EXPIRED = 'expired'


class DiscoveryJobDetail(APIModel):
    id: UUID4Str
    run: UUID4Str
    collector: UUID4Str
    collector_name: str
    status: DiscoveryJobStatusEnum
    canonical_devices: list[dict]
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
    cancellation_acknowledged_at: datetime | None


PaginatedDiscoveryJobList = PaginatedResponse[DiscoveryJobDetail]


class InventoryMeta(BaseModel):
    hostvars: dict[str, dict]


class InventoryAll(BaseModel):
    hosts: list[str]


class DiscoveryJobInventory(BaseModel):
    _meta: InventoryMeta
    all: InventoryAll


class DiscoveryJobClaim(APIModel):
    id: UUID4Str
    run: UUID4Str
    claim_token: str
    idempotency_key: str
    inventory: dict

    @field_validator('inventory')
    @classmethod
    def validate_inventory(cls, inventory: dict) -> dict:
        DiscoveryJobInventory.model_validate(inventory)
        return inventory  # Return original inventory


class DiscoveryJobPush(APIModel):
    status: DiscoveryJobStatusEnum
    attempt: int
    max_attempts: int
    claimed_at: datetime | None
    last_heartbeat_at: datetime | None
    lease_expires_at: datetime | None
    timeout_at: datetime | None
    created_at: datetime
    updated_at: datetime
    cancellation_acknowledged_at: datetime | None


# ---------------------------------------------------------------------------
# discovery.RawOutput
# ---------------------------------------------------------------------------


class RawOutputStatusEnum(Enum):
    """Discovery job lifecycle statuses."""

    FAILED = 'failed'
    IGNORED_AFTER_CANCEL = 'ignored_after_cancel'
    PARSED = 'parsed'
    QUEUED = 'queued'
    RECEIVED = 'received'
    STALE = 'stale'


class RawOutputList(APIModel):
    id: UUID4Str
    attempt: int
    canonical_device: UUID4Str
    idempotency_key: str
    job: UUID4Str
    log_messages: list[str]
    run: UUID4Str
    status: RawOutputStatusEnum
    created_at: datetime
    processed_at: datetime | None
    updated_at: datetime


PaginatedRawOutputList = PaginatedResponse[RawOutputList]
