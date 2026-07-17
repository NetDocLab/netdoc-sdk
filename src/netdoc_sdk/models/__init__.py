"""Pydantic models for the NetDoc API contracts.

This package contains the request and response models used by the SDK. Models are
organized by functional area and are intended to provide a typed interface for
working with NetDoc resources.

Modules:
    - core: Shared base models and common enums
    - discovery: Credentials, collectors, and discovery-job models
    - inventory: Sites, devices, interfaces, and related inventory models
    - snapshots: Snapshot-related models

Model patterns:
    - Detail models: Full resource representations returned by the API
    - Create/Update models: Payloads used for write operations
    - Paginated models: List responses with pagination metadata
    - Enums: Predefined value choices

All models are Pydantic v2 ``BaseModel`` subclasses with:
    - type hints and validation
    - automatic coercion for common values such as UUIDs and datetimes
    - tolerance for extra API fields, with warnings when relevant
    - support for ``populate_by_name`` and API field aliases

Example:
    from netdoc_sdk.models.snapshots import SnapshotDetail
    from netdoc_sdk.models.inventory import SiteCreate

    snapshot: SnapshotDetail = ...  # From API
    site_data = SiteCreate(name="Site A")  # For creating
"""
