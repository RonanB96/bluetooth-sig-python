"""Types for Bluetooth SIG SDP Base UUID registry."""

from __future__ import annotations

from msgspec import Struct


class SdpBaseUuidInfo(Struct, frozen=True, kw_only=True):
    """Information about the Bluetooth SDP base UUID."""

    name: str
    uuid: str
