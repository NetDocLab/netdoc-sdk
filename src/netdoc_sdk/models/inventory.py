"""Pydantic models matching the public NetDoc OpenAPI inventory contracts."""

from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Any, List
from pydantic import Field
from netdoc_sdk.models.core import APIModel, PaginatedResponse, UUID4Str


# ---------------------------------------------------------------------------
# inventory.Site
# ---------------------------------------------------------------------------


class SiteTypeEnum(str, Enum):
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


# ---------------------------------------------------------------------------
# inventory.CanonicalDevice
# ---------------------------------------------------------------------------


# class CanonicalDevice(APIModel):
#     id: str
#     primary_serial: str = ''
#     primary_hostname: str = ''
#     instance_id: str = ''
#     parent_serial: str = ''
#     mgmt_ip: str | None = None
#     first_seen: datetime
#     last_seen: datetime
#     is_active: bool = True
#     inactive_since: datetime | None = None


# class CanonicalEndpoint(APIModel):
#     id: str
#     instance_id: str = ''
#     hypervisor_type: HypervisorTypeEnum | str | None = None
#     primary_mac: str = ''
#     primary_hostname: str = ''
#     first_seen: datetime
#     last_seen: datetime
#     is_active: bool = True
#     inactive_since: datetime | None = None
