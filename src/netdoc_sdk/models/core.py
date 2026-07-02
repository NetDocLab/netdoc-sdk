"""Pydantic models matching the public NetDoc OpenAPI core contracts."""

import logging
import os
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator

_STRICT_EXTRA = os.getenv('SDK_STRICT', '').lower() in ('1', 'true', 'yes', 'on')

logger = logging.getLogger('netdoc_sdk')


class Severity(Enum):
    DEBUG = 'DEBUG'
    ERROR = 'ERROR'
    INFO = 'INFO'
    WARNING = 'WARNING'


class APIModel(BaseModel):
    """Base model that tolerates additive API fields logging them."""

    model_config = ConfigDict(extra='forbid' if _STRICT_EXTRA else 'ignore', populate_by_name=True)

    @model_validator(mode='before')
    @classmethod
    def _warn_extra_fields(cls, values: Any) -> Any:
        if isinstance(values, dict):
            known = cls.model_fields.keys()
            for key in values:
                if key not in known:
                    logger.warning(
                        'Unexpected field %r in %s response (SDK may be outdated)',
                        key,
                        cls.__name__,
                    )
        return values
