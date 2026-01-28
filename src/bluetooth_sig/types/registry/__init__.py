"""Core types for Bluetooth SIG registry data structures."""

from __future__ import annotations

__all__ = [
    "AdTypeInfo",
    "BaseUuidInfo",
    "CharacteristicSpec",
    "FieldInfo",
    "KeyNameInfo",
    "NameOpcodeTypeInfo",
    "NameUuidTypeInfo",
    "NameValueInfo",
    "UnitMetadata",
    "UuidIdInfo",
    "ValueNameInfo",
    "ValueNameReferenceInfo",
    "generate_basic_aliases",
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
