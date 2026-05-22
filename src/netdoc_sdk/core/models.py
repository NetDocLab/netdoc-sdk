"""Pydantic models matching the public NetDoc OpenAPI core contract."""

from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Any, Generic, TypeVar
from collections.abc import Mapping
from pydantic import BaseModel, ConfigDict, Field


T = TypeVar('T')

JsonMapping = Mapping[str, Any] | BaseModel


class Severity(str, Enum):
    DEBUG = "DEBUG"
    ERROR = "ERROR"
    INFO = "INFO"
    WARNING = "WARNING"


class APIModel(BaseModel):
    """Base model that tolerates additive API fields without dropping them."""

    model_config = ConfigDict(extra='forbid', populate_by_name=True)


class PaginatedResponse(APIModel, Generic[T]):
    """DRF-style paginated response."""

    count: int
    next: str | None = None
    previous: str | None = None
    results: list[T]


class LogMessage(APIModel):
    message: str
    severity: Severity
    timestamp: datetime


class MetadataModel(BaseModel):
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
# core.Tenant
# ---------------------------------------------------------------------------


class TenantDetail(APIModel):
    id: UUID
    name: str = ''
    is_active: bool = False
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class TenantList(APIModel):
    id: UUID
    name: str = ''
    is_active: bool = False
    # Metadata
    created_at: datetime
    updated_at: datetime


PaginatedTenantList = PaginatedResponse[TenantList]


class TenantCreate(APIModel):
    name: str
    is_active: bool = True
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


class RoleEnum(str, Enum):
    ADMIN = 'admin'
    COLLECTOR = 'collector'
    OPERATOR = 'operator'
    VIEWER = 'viewer'


class UserDetail(APIModel):
    id: UUID
    username: str = ''
    role: RoleEnum = RoleEnum.VIEWER
    email: str = ''
    first_name: str = ''
    last_name: str = ''
    is_active: bool = False
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    last_login: datetime | None = None
    updated_at: datetime


class UserList(APIModel):
    id: UUID
    username: str = ''
    role: RoleEnum = RoleEnum.VIEWER
    email: str = ''
    first_name: str = ''
    last_name: str = ''
    is_active: bool = False
    # Metadata
    created_at: datetime
    last_login: datetime | None = None
    updated_at: datetime


PaginatedUserList = PaginatedResponse[UserList]


class UserCreate(APIModel):
    username: str
    password: str
    role: RoleEnum = RoleEnum.VIEWER
    email: str = ''
    first_name: str = ''
    last_name: str = ''
    is_active: bool = True
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)


class UserUpdate(APIModel):
    username: str | None = None
    password: str | None = None
    role: RoleEnum | str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    # Metadata
    metadata: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# core.AuditLog
# ---------------------------------------------------------------------------


class AuditLogDetail(APIModel):
    id: UUID
    source_ip: str = ''
    user: str = ''
    username: str = ''
    tenant: UUID | None = None
    action: str = ''
    resource_path: str = ''
    status_code: int = 0
    duration_ms: float = 0
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class AuditLogList(APIModel):
    id: UUID
    source_ip: str = ''
    user: str = ''
    username: str = ''
    tenant: UUID | None = None
    action: str = ''
    resource_path: str = ''
    status_code: int = 0
    # Metadata
    created_at: datetime


PaginatedAuditLogList = PaginatedResponse[AuditLogList]
