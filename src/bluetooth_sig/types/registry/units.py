from __future__ import annotations

import msgspec

from bluetooth_sig.types.registry import BaseUuidInfo


class UnitEntry(msgspec.Struct, frozen=True):
    """Entry for units from YAML."""

    uuid: str
    name: str
    id: str


class UnitsData(msgspec.Struct):
    """Top-level data structure for units.yaml."""

    uuids: list[UnitEntry]


class UnitInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG unit."""

    summary: str = ""
