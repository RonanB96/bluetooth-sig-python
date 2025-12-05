"""Types for Bluetooth SIG member UUID registry."""

from __future__ import annotations

from bluetooth_sig.types.registry import BaseUuidInfo


class MemberInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG member UUID.

    Member UUIDs only have uuid and name in the YAML.
    """
