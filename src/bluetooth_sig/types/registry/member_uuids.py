from __future__ import annotations

import msgspec

from bluetooth_sig.types.registry import BaseUuidInfo


class MemberUuidEntry(msgspec.Struct, frozen=True):
    """Entry for member UUIDs from YAML."""

    uuid: str
    name: str


class MemberUuidsData(msgspec.Struct):
    """Top-level data structure for member_uuids.yaml."""

    uuids: list[MemberUuidEntry]


class MemberInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG member company."""

    summary: str = ""
