"""Pydantic models matching the public NetDoc OpenAPI inventory contracts."""

from datetime import datetime
from enum import Enum

from netdoc_sdk.models.core import APIModel, PaginatedResponse, UUID4Str

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
    site_type: SiteTypeEnum
    address: str
    city: str
    region: str
    country: str
    created_at: datetime
    updated_at: datetime


class SiteList(APIModel):
    id: UUID4Str
    name: str
    site_type: SiteTypeEnum | None
    address: str
    city: str
    region: str
    country: str
    created_at: datetime
    updated_at: datetime


PaginatedSiteList = PaginatedResponse[SiteList]


class SiteCreate(APIModel):
    name: str
    site_type: SiteTypeEnum | None = None
    address: str | None = None
    city: str | None = None
    region: str | None = None
    country: str | None = None


class SiteUpdate(APIModel):
    name: str | None = None
    site_type: SiteTypeEnum | None = None
    address: str | None = None
    city: str | None = None
    region: str | None = None
    country: str | None = None


# ---------------------------------------------------------------------------
# inventory.CanonicalDevice
# ---------------------------------------------------------------------------


class CanonicalDeviceDetail(APIModel):
    id: UUID4Str
    label: str
    mgmt_address: str | None
    discovery_mode: str | None
    is_discoverable: bool
    identifiers: dict
    credential: UUID4Str | None
    parent: UUID4Str | None
    site: UUID4Str | None
    site_name: str | None
    role: str | None
    created_at: datetime
    updated_at: datetime
    first_seen: datetime | None
    last_seen: datetime | None
    inactive_since: datetime | None
    is_active: bool


class CanonicalDeviceList(APIModel):
    id: UUID4Str
    label: str
    mgmt_address: str | None
    discovery_mode: str | None
    is_discoverable: bool
    parent: UUID4Str | None
    site: UUID4Str | None
    site_name: str | None
    role: str | None
    created_at: datetime
    updated_at: datetime
    first_seen: datetime | None
    last_seen: datetime | None
    inactive_since: datetime | None
    is_active: bool


PaginatedCanonicalDeviceList = PaginatedResponse[CanonicalDeviceList]


class CanonicalDeviceCreate(APIModel):
    label: str
    mgmt_address: str | None = None
    is_discoverable: bool
    identifiers: list
    credential: UUID4Str | None = None
    parent: UUID4Str | None = None
    site: UUID4Str | None = None
    role: str | None = None


class CanonicalDeviceUpdate(APIModel):
    label: str | None = None
    mgmt_address: str | None = None
    is_discoverable: bool
    identifiers: list | None = None
    credential: UUID4Str | None = None
    parent: UUID4Str | None = None
    site: UUID4Str | None = None
    role: str | None = None
