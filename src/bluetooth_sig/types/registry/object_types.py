"""Types for Bluetooth SIG object types registry."""

from __future__ import annotations

from bluetooth_sig.types.registry import BaseUuidInfo


class ObjectTypeInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG object type."""

    id: str
