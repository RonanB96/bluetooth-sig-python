from __future__ import annotations

import msgspec

from bluetooth_sig.types.registry import BaseUuidInfo


class BrowseGroupIdentifierEntry(msgspec.Struct, frozen=True):
    """Entry for browse group identifiers from YAML."""

    uuid: str
    name: str
    id: str


class BrowseGroupIdentifiersData(msgspec.Struct):
    """Top-level data structure for browse_group_identifiers.yaml."""

    uuids: list[BrowseGroupIdentifierEntry]


class BrowseGroupInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG browse group identifier."""

    summary: str = ""
