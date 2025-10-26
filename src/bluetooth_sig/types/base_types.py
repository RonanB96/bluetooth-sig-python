"""Base data types shared across the library."""

from __future__ import annotations

import msgspec

from .uuid import BluetoothUUID


class SIGInfo(msgspec.Struct, kw_only=True):
    """Base information about Bluetooth SIG characteristics or services."""

    uuid: BluetoothUUID
    name: str
    description: str = ""
