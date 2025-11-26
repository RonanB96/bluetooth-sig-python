from __future__ import annotations

import msgspec

from bluetooth_sig.types.registry import BaseUuidInfo


class SdoUuidEntry(msgspec.Struct, frozen=True):
    """Entry for SDO UUIDs from YAML."""

    uuid: str
    name: str


class SdoUuidsData(msgspec.Struct):
    """Top-level data structure for sdo_uuids.yaml."""

    uuids: list[SdoUuidEntry]


class SdoUuidInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG SDO UUID."""

    summary: str = ""
