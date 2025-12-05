"""Types for Bluetooth SIG characteristic UUID registry."""

from __future__ import annotations

from bluetooth_sig.types.registry import BaseUuidInfo


class CharacteristicUuidInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG characteristic UUID."""

    id: str
    summary: str = ""
