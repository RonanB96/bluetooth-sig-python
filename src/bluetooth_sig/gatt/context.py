"""Context objects used during characteristic parsing.

This module provides a small, well-typed container that parsers can use to
access device-level information, advertisement data, and already-parsed
characteristics when decoding values that depend on context.
"""

from __future__ import annotations

# Re-export context types from the types package to maintain backward compatibility
from ..types import CharacteristicContext, CharacteristicDataProtocol, DeviceInfo

__all__ = ["CharacteristicContext", "CharacteristicDataProtocol", "DeviceInfo"]
