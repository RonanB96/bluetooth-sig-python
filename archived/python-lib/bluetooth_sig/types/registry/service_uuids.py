"""Types for Bluetooth SIG service UUID registry."""

from __future__ import annotations

from bluetooth_sig.types.registry import BaseUuidInfo


class ServiceUuidInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG service UUID."""

    id: str
    summary: str = ""
