from __future__ import annotations

import msgspec

from bluetooth_sig.types.registry import BaseUuidInfo


class DeclarationEntry(msgspec.Struct, frozen=True):
    """Entry for declarations from YAML."""

    uuid: str
    name: str
    id: str


class DeclarationsData(msgspec.Struct):
    """Top-level data structure for declarations.yaml."""

    uuids: list[DeclarationEntry]


class DeclarationInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG GATT attribute declaration."""

    summary: str = ""
