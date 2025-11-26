from __future__ import annotations

import msgspec

from bluetooth_sig.types.registry import BaseUuidInfo


class ServiceUuidEntry(msgspec.Struct, frozen=True):
    """Entry for service UUIDs from YAML."""

    uuid: str
    name: str
    id: str


class ServiceUuidsData(msgspec.Struct):
    """Top-level data structure for service_uuids.yaml."""

    uuids: list[ServiceUuidEntry]


class ServiceUuidInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG service UUID."""

    summary: str = ""
