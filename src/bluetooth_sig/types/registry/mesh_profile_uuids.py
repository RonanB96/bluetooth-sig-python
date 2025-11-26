from __future__ import annotations

import msgspec

from bluetooth_sig.types.registry import BaseUuidInfo


class MeshProfileUuidEntry(msgspec.Struct, frozen=True):
    """Entry for mesh profile UUIDs from YAML."""

    uuid: str
    name: str
    id: str


class MeshProfileUuidsData(msgspec.Struct):
    """Top-level data structure for mesh_profile_uuids.yaml."""

    uuids: list[MeshProfileUuidEntry]


class MeshProfileInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG mesh profile."""

    summary: str = ""
