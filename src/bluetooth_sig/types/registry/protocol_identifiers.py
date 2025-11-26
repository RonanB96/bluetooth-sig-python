from __future__ import annotations

import msgspec

from bluetooth_sig.types.registry import BaseUuidInfo


class ProtocolIdentifierEntry(msgspec.Struct, frozen=True):
    """Entry for protocol identifiers from YAML."""

    uuid: str
    name: str
    id: str


class ProtocolIdentifiersData(msgspec.Struct):
    """Top-level data structure for protocol_identifiers.yaml."""

    uuids: list[ProtocolIdentifierEntry]


class ProtocolInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth protocol identifier."""

    summary: str = ""
