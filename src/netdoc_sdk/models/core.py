"""Pydantic models matching the public NetDoc OpenAPI core contracts."""

from datetime import datetime
from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from pydantic.functional_validators import AfterValidator


class Severity(Enum):
    DEBUG = 'DEBUG'
    ERROR = 'ERROR'
    INFO = 'INFO'
    WARNING = 'WARNING'


class APIModel(BaseModel):
    """Base model that tolerates additive API fields without dropping them."""

    model_config = ConfigDict(extra='forbid', populate_by_name=True)


class PaginatedResponse[T](APIModel):
    """DRF-style paginated response."""

    count: int
    next: str | None = None
    previous: str | None = None
    results: list[T]


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------


def validate_uuid4_str(v: str) -> str:
    u = UUID(v)

    if u.version != 4:
        raise ValueError('UUID must be v4')

    return v


UUID4Str = Annotated[str, AfterValidator(validate_uuid4_str)]


class LogMessage(APIModel):
    message: str
    severity: Severity
    timestamp: datetime


# ---------------------------------------------------------------------------
# core.Tenant
# ---------------------------------------------------------------------------


class TenantDetail(APIModel):
    id: UUID4Str
    name: str
    is_active: bool
    log_retention_days: int
    max_snapshots: int
    snapshot_retention_days: int
    created_at: datetime
    updated_at: datetime


class TenantList(APIModel):
    id: UUID4Str
    name: str
    is_active: bool
    log_retention_days: int
    max_snapshots: int
    snapshot_retention_days: int
    created_at: datetime
    updated_at: datetime


PaginatedTenantList = PaginatedResponse[TenantList]


class TenantCreate(APIModel):
    name: str
    is_active: bool | None = None
    log_retention_days: int | None = None
    max_snapshots: int | None = None
    snapshot_retention_days: int | None = None


class TenantUpdate(APIModel):
    name: str | None = None
    is_active: bool | None = None
    log_retention_days: int | None = None
    max_snapshots: int | None = None
    snapshot_retention_days: int | None = None


# ---------------------------------------------------------------------------
# core.User
# ---------------------------------------------------------------------------


class RoleEnum(Enum):
    ADMIN = 'admin'
    COLLECTOR = 'collector'
    OPERATOR = 'operator'
    VIEWER = 'viewer'


class UserDetail(APIModel):
    id: UUID4Str
    username: str
    role: RoleEnum | None
    is_active: bool
    first_name: str
    last_name: str
    email: str
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None


class UserList(APIModel):
    id: UUID4Str
    username: str
    is_active: bool
    role: RoleEnum | None
    first_name: str
    last_name: str
    email: str
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None


PaginatedUserList = PaginatedResponse[UserList]


class UserCreate(APIModel):
    username: str
    password: str
    role: RoleEnum | None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    is_active: bool | None = None


class UserUpdate(APIModel):
    username: str | None = None
    password: str | None = None
    role: RoleEnum | None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    is_active: bool | None = None


class UserProfileUpdate(APIModel):
    password: str | None = None


# ---------------------------------------------------------------------------
# core.Token
# ---------------------------------------------------------------------------


class TokenDetail(APIModel):
    token: str


class TokenRequest(APIModel):
    username: str
    password: str


# ---------------------------------------------------------------------------
# core.AuditLog
# ---------------------------------------------------------------------------


class AuditLogDetail(APIModel):
    id: UUID4Str
    tenant: UUID | None
    source_ip: str
    user: str
    username: str
    action: str
    resource_path: str
    status_code: int
    duration_ms: float
    created_at: datetime


class AuditLogList(APIModel):
    id: UUID4Str
    tenant: UUID | None
    source_ip: str
    user: str
    username: str
    action: str
    resource_path: str
    status_code: int
    created_at: datetime


PaginatedAuditLogList = PaginatedResponse[AuditLogList]
