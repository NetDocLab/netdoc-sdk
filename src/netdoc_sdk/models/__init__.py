"""NetDoc SDK Pydantic models for API contracts.

This package contains Pydantic models for all API request and response types.
Models are organized by functional area:

Modules:
    - core: User, tenant, token, and audit log models
    - snapshots: Snapshot and snapshot-related models
    - discovery: Credentials, collectors, and discovery job models
    - inventory: Network inventory models (sites, devices, interfaces, etc.)

Model Patterns:
    - Detail models: Full resource representation (read from API)
    - Create/Update models: Request payloads (write to API)
    - Paginated models: List responses with pagination metadata
    - Enums: Predefined value choices

All models are Pydantic v2 BaseModel subclasses with:
    - Type hints and validation
    - Automatic coercion (str → UUID, str → datetime)
    - Extra field tolerance (logs unexpected API fields)
    - Support for populate_by_name (API field aliases)

Example:
    from netdoc_sdk.models.snapshots import SnapshotDetail
    from netdoc_sdk.models.inventory import SiteCreate

    snapshot: SnapshotDetail = ...  # From API
    site_data = SiteCreate(name="Site A")  # For creating
"""
