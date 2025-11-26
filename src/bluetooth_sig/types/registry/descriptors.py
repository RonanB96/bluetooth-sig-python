from __future__ import annotations

import msgspec

from bluetooth_sig.types.registry import BaseUuidInfo


class DescriptorEntry(msgspec.Struct, frozen=True):
    """Entry for descriptors from YAML."""

    uuid: str
    name: str
    id: str


class DescriptorsData(msgspec.Struct):
    """Top-level data structure for descriptors.yaml."""

    uuids: list[DescriptorEntry]


class DescriptorInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG descriptor."""

    summary: str = ""
