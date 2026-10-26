"""Types for Bluetooth SIG descriptor registry."""

from __future__ import annotations

from bluetooth_sig.types.registry import BaseUuidInfo


class DescriptorInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG descriptor."""

    id: str
    summary: str = ""
