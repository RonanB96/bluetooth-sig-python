"""Types for Bluetooth SIG Device Property IDs registry."""

from __future__ import annotations

import msgspec

from bluetooth_sig.types.registry import BaseUuidInfo


class PropertyIdEntry(msgspec.Struct, frozen=True):
    """Entry for property IDs from YAML."""

    identifier: str
    propertyid: str


class PropertyIdsData(msgspec.Struct):
    """Top-level data structure for property_ids.yaml."""

    propertyids: list[PropertyIdEntry]


class PropertyIdInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG property ID."""

    summary: str = ""
