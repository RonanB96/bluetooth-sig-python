"""GATT descriptors package.

Descriptor classes are lazy-loaded via PEP 562 ``__getattr__`` to keep
package import lightweight. Built-in descriptors register on first
registry access.
"""

from __future__ import annotations

from ..lazy_exports import lazy_getattr
from .base import BaseDescriptor
from .registry import DescriptorRegistry

try:
    from ._export_map import LAZY_EXPORT_MAP
except ImportError:
    LAZY_EXPORT_MAP = {}

_EAGER_EXPORTS = ("BaseDescriptor", "DescriptorRegistry")

__all__ = [
    *_EAGER_EXPORTS,
    *LAZY_EXPORT_MAP,
]


def __getattr__(name: str) -> object:
    return lazy_getattr(__name__, LAZY_EXPORT_MAP, name)


def __dir__() -> list[str]:
    return sorted(__all__)
