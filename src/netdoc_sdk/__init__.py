"""NetDoc SDK."""

from netdoc_sdk.client import NetDocClient
from netdoc_sdk.exceptions import (  # noqa: F401
    AuthenticationError,
    ConnectionError,
    MethodNotAllowedError,
    NetDocError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from netdoc_sdk.models import core as _core  # noqa: F401
from netdoc_sdk.models import discovery as _discovery  # noqa: F401
from netdoc_sdk.models import inventory as _inventory  # noqa: F401
from netdoc_sdk.models import snapshots as _snapshots  # noqa: F401

models = []
for model in ['_core', '_snapshots', '_discovery', '_inventory']:
    models += [name for name in dir(model) if not name.startswith('_')]
    del model


__all__ = [
    'AuthenticationError',
    'ConnectionError',
    'MethodNotAllowedError',
    'NetDocClient',
    'NetDocError',
    'NotFoundError',
    'PermissionDeniedError',
    'SnapshotError',
    'ValidationError',
    *models,
]
