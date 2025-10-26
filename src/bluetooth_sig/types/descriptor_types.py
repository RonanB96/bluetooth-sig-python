"""Data types for Bluetooth SIG descriptors."""

from __future__ import annotations

from typing import Any

import msgspec

from .base_types import SIGInfo
from .uuid import BluetoothUUID


class DescriptorInfo(SIGInfo):
    """Information about a Bluetooth descriptor."""

    # Descriptors may have structured data parsing requirements
    has_structured_data: bool = False
    data_format: str = ""  # e.g., "uint16", "struct", etc.


class DescriptorData(msgspec.Struct, kw_only=True):
    """Parsed descriptor data with validation results."""

    info: DescriptorInfo
    value: Any | None = None
    raw_data: bytes = b""
    parse_success: bool = False
    error_message: str = ""

    @property
    def name(self) -> str:
        """Get the descriptor name from info."""
        return self.info.name

    @property
    def uuid(self) -> BluetoothUUID:
        """Get the descriptor UUID from info."""
        return self.info.uuid
