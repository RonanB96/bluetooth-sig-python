"""Protocol definitions for Bluetooth SIG standards."""

from __future__ import annotations

from typing import Protocol


class CharacteristicProtocol(Protocol):
    """Protocol for characteristic validation and round-trip testing.

    Defines the minimal interface for characteristics that support
    parse/encode operations without requiring full BaseCharacteristic import.
    Used primarily by debug utilities.
    """

    def _decode_value(self, data: bytearray) -> object:
        """Decode raw data into characteristic value."""
        ...  # pylint: disable=unnecessary-ellipsis

    def parse_value(self, data: bytearray) -> object:
        """Parse raw data into characteristic value."""
        ...  # pylint: disable=unnecessary-ellipsis

    def build_value(self, data: object, validate: bool = True) -> bytearray:
        """Encode characteristic value into raw bytes."""
        ...  # pylint: disable=unnecessary-ellipsis

    def _encode_value(self, value: object) -> bytearray:
        """Internal encoding implementation."""
        ...  # pylint: disable=unnecessary-ellipsis
