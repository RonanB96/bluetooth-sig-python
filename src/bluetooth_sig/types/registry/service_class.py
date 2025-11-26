from __future__ import annotations

import msgspec

from bluetooth_sig.types.registry import BaseUuidInfo


class ServiceClassEntry(msgspec.Struct, frozen=True):
    """Entry for service class from YAML."""

    uuid: str
    name: str
    id: str


class ServiceClassData(msgspec.Struct):
    """Top-level data structure for service_class.yaml."""

    uuids: list[ServiceClassEntry]


class ServiceClassInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG service class."""

    summary: str = ""
