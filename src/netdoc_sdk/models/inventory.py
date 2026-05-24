"""Pydantic models matching the public NetDoc OpenAPI inventory contracts."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field

from netdoc_sdk.models.core import APIModel, PaginatedResponse, UUID4Str
from pydantic_core.core_schema import UuidSchema


# ---------------------------------------------------------------------------
# inventory.CanonicalDevice
# ---------------------------------------------------------------------------


class CanonicalDeviceDetail(APIModel):
    id: UUID4Str
    label: str
    mgmt_address: str | None = None
    discovery_mode: str | None = None
    is_discoverable: bool
    identifiers: dict
    credential: UUID4Str | None = None
    parent: UUID4Str | None = None
    role: str | None = None
    site: UUID4Str | None = None
    site_name: str | None = None
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)
    is_active: bool
    created_at: datetime
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    updated_at: datetime


class CanonicalDeviceList(APIModel):
    id: UUID4Str
    label: str
    mgmt_address: str | None = None
    discovery_mode: str | None = None
    is_discoverable: bool
    credential: UUID4Str | None = None
    parent: UUID4Str | None = None
    site: UUID4Str | None = None
    site_name: str | None = None
    # Metadata
    is_active: bool
    created_at: datetime
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    updated_at: datetime


PaginatedCanonicalDeviceList = PaginatedResponse[CanonicalDeviceList]


class CanonicalDeviceCreate(APIModel):
    label: str
    mgmt_address: str | None = None
    is_discoverable: bool
    identifiers: list
    credential: UUID4Str | None = None
    parent: UUID4Str | None = None
    role: str | None = None
    site: UUID4Str | None = None
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)


class CanonicalDeviceUpdate(APIModel):
    label: str | None = None
    mgmt_address: str | None = None
    is_discoverable: bool
    identifiers: list
    credential: UUID4Str | None = None
    parent: UUID4Str | None = None
    role: str | None = None
    site: UUID4Str | None = None
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# inventory.Site
# ---------------------------------------------------------------------------


class SiteTypeEnum(Enum):
    DATACENTER = 'datacenter'
    CAMPUS = 'campus'
    CLOUD = 'cloud'
    BRANCH = 'branch'
    OTHER = 'other'


class SiteDetail(APIModel):
    id: UUID4Str
    name: str
    site_type: SiteTypeEnum | str = SiteTypeEnum.OTHER
    address: str = ''
    city: str = ''
    region: str = ''
    country: str = ''
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class SiteList(APIModel):
    id: UUID4Str
    name: str
    site_type: SiteTypeEnum | str = SiteTypeEnum.OTHER
    address: str = ''
    city: str = ''
    region: str = ''
    country: str = ''
    # Metadata
    created_at: datetime
    updated_at: datetime


PaginatedSiteList = PaginatedResponse[SiteList]


class SiteCreate(APIModel):
    name: str
    site_type: SiteTypeEnum | str = SiteTypeEnum.OTHER
    address: str = ''
    city: str = ''
    region: str = ''
    country: str = ''
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)


class SiteUpdate(APIModel):
    name: str
    site_type: SiteTypeEnum | str = SiteTypeEnum.OTHER
    address: str = ''
    city: str = ''
    region: str = ''
    country: str = ''
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)
