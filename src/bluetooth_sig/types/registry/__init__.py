"""Core types for Bluetooth SIG registry data structures."""

from __future__ import annotations

__all__ = [
    "AdTypeInfo",
    "BaseUuidInfo",
    "FieldInfo",
    "UnitMetadata",
    "CharacteristicSpec",
    "generate_basic_aliases",
    "UuidIdInfo",
    "ValueNameInfo",
    "ValueNameReferenceInfo",
    "NameValueInfo",
    "KeyNameInfo",
    "NameUuidTypeInfo",
    "NameOpcodeTypeInfo",
]

from .ad_types import AdTypeInfo
from .common import (
    BaseUuidInfo,
    CharacteristicSpec,
    FieldInfo,
    KeyNameInfo,
    NameOpcodeTypeInfo,
    NameUuidTypeInfo,
    NameValueInfo,
    UnitMetadata,
    UuidIdInfo,
    ValueNameInfo,
    ValueNameReferenceInfo,
    generate_basic_aliases,
)
