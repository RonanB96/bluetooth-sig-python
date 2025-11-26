from __future__ import annotations

import msgspec

from bluetooth_sig.types.registry import BaseUuidInfo


class ObjectTypeEntry(msgspec.Struct, frozen=True):
    """Entry for object types from YAML."""

    uuid: str
    name: str
    id: str


class ObjectTypesData(msgspec.Struct):
    """Top-level data structure for object_types.yaml."""

    uuids: list[ObjectTypeEntry]


class ObjectTypeInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG object type."""

    summary: str = ""
