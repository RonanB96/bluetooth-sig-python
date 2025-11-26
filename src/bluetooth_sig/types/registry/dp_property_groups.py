from __future__ import annotations

import msgspec

from bluetooth_sig.types.registry import BaseUuidInfo


class PropertyGroupEntry(msgspec.Struct, frozen=True):
    """Entry for property groups from YAML."""

    identifier: str
    name: str
    description: str


class PropertyGroupsData(msgspec.Struct):
    """Top-level data structure for property_groups.yaml."""

    groups: list[PropertyGroupEntry]


class PropertyGroupInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG property group."""

    description: str = ""
    summary: str = ""
