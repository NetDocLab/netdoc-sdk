"""Pydantic models matching the public NetDoc OpenAPI core contracts."""

from datetime import datetime
from enum import Enum
from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
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
    # Metadata
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class TenantList(APIModel):
    id: UUID4Str
    name: str
    is_active: bool
    # Metadata
    created_at: datetime
    updated_at: datetime


PaginatedTenantList = PaginatedResponse[TenantList]


class TenantCreate(APIModel):
    name: str
    is_active: bool | None = None
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)


class TenantUpdate(APIModel):
    name: str | None = None
    is_active: bool | None = None
    # Metadata
    metadata: dict[str, Any] | None = None


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
    email: str
    first_name: str
    last_name: str
    is_active: bool
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    last_login: datetime | None
    updated_at: datetime


class UserList(APIModel):
    id: UUID4Str
    username: str
    role: RoleEnum | None
    email: str
    first_name: str
    last_name: str
    is_active: bool
    # Metadata
    created_at: datetime
    last_login: datetime | None
    updated_at: datetime


PaginatedUserList = PaginatedResponse[UserList]


class UserCreate(APIModel):
    username: str
    password: str
    role: RoleEnum | None
    email: str = ''
    first_name: str = ''
    last_name: str = ''
    is_active: bool | None = None
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)


class UserUpdate(APIModel):
    username: str | None = None
    password: str | None = None
    role: RoleEnum | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    # Metadata
    metadata: dict[str, Any] | None = None


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
    source_ip: str
    user: str
    username: str
    tenant: UUID | None
    action: str
    resource_path: str
    status_code: int
    duration_ms: float
    # Metadata
    metadata: dict[str, Any]
    created_at: datetime


class AuditLogList(APIModel):
    id: UUID4Str
    source_ip: str
    user: str
    username: str
    tenant: UUID | None
    action: str
    resource_path: str
    status_code: int
    # Metadata
    created_at: datetime


PaginatedAuditLogList = PaginatedResponse[AuditLogList]
