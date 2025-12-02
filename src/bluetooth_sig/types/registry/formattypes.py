"""Types for Bluetooth SIG Format Types registry."""

from __future__ import annotations

from msgspec import Struct


class FormatTypeInfo(Struct, frozen=True, kw_only=True):
    """Information about a Bluetooth characteristic format type."""

    value: int
    short_name: str
    description: str
    exponent: bool
    size: int
