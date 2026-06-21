"""Registry of supported GATT services.

Service classes are lazy-loaded via PEP 562 ``__getattr__`` to keep
package import lightweight.
"""

from __future__ import annotations

from ..lazy_exports import lazy_getattr
from .base import (
    CharacteristicStatus,
    ServiceCharacteristicInfo,
    ServiceCompletenessReport,
    ServiceHealthStatus,
    ServiceValidationResult,
)
from .registry import GattServiceRegistry, ServiceName, get_service_class_map

try:
    from ._export_map import LAZY_EXPORT_MAP, LAZY_EXPORT_NAMES
except ImportError:
    LAZY_EXPORT_MAP = {}
    LAZY_EXPORT_NAMES = ()

_EAGER_EXPORTS = (
    "CharacteristicStatus",
    "GattServiceRegistry",
    "ServiceCharacteristicInfo",
    "ServiceCompletenessReport",
    "ServiceHealthStatus",
    "ServiceName",
    "ServiceValidationResult",
    "get_service_class_map",
)

__all__ = [
    *_EAGER_EXPORTS,
    *LAZY_EXPORT_NAMES,
]


def __getattr__(name: str) -> object:
    return lazy_getattr(__name__, LAZY_EXPORT_MAP, name)


def __dir__() -> list[str]:
    return sorted(__all__)
