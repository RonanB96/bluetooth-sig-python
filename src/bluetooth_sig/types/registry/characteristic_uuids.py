from __future__ import annotations

import msgspec

from bluetooth_sig.types.registry import BaseUuidInfo


class CharacteristicUuidEntry(msgspec.Struct, frozen=True):
    """Entry for characteristic UUIDs from YAML."""

    uuid: str
    name: str
    id: str


class CharacteristicUuidsData(msgspec.Struct):
    """Top-level data structure for characteristic_uuids.yaml."""

    uuids: list[CharacteristicUuidEntry]


class CharacteristicUuidInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG characteristic UUID."""

    summary: str = ""
