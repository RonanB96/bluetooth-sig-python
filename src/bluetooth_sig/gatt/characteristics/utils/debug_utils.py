"""Debugging and testing support utilities."""

from __future__ import annotations

import struct
from typing import Any

from .bit_field_utils import BitFieldUtils


class DebugUtils:
    """Utility class for debugging and testing support."""

    # Format constants
    HEX_FORMAT_WIDTH = 2
    DEFAULT_PRECISION = 2

    @staticmethod
    def format_hex_dump(data: bytearray) -> str:
        """Format data as a hex dump for debugging."""
        return " ".join(f"{byte:02X}" for byte in data)  # HEX_FORMAT_WIDTH = 2

    @staticmethod
    def validate_round_trip(characteristic: Any, original_data: bytearray) -> bool:
        """Validate that parse/encode operations preserve data integrity."""
        try:
            parsed = characteristic.parse_value(original_data)
            encoded = characteristic.encode_value(parsed)
            return bool(original_data == encoded)
        except Exception:  # pylint: disable=broad-except
            return False

    @staticmethod
    def format_measurement_value(
        value: Any,
        unit: str | None = None,
        precision: int = 2,  # DebugUtils.DEFAULT_PRECISION,
    ) -> str:
        """Format measurement value with unit for display."""
        if value is None:
            return "N/A"

        if isinstance(value, float):
            formatted = f"{value:.{precision}f}"
        else:
            formatted = str(value)

        if unit:
            return f"{formatted} {unit}"
        return formatted

    @staticmethod
    def format_hex_data(data: bytes | bytearray, separator: str = " ") -> str:
        """Format binary data as hex string."""
        return separator.join(f"{byte:02X}" for byte in data)  # HEX_FORMAT_WIDTH = 2

    @staticmethod
    def format_binary_flags(value: int, bit_names: list[str]) -> str:
        """Format integer as binary flags with names."""
        flags: list[str] = []
        for i, name in enumerate(bit_names):
            if BitFieldUtils.test_bit(value, i):
                flags.append(name)
        return ", ".join(flags) if flags else "None"

    @staticmethod
    def validate_struct_format(data: bytes | bytearray, format_string: str) -> None:
        """Validate data length matches struct format requirements."""
        expected_size = struct.calcsize(format_string)
        actual_size = len(data)
        if actual_size != expected_size:
            raise ValueError(
                f"Data size {actual_size} doesn't match format '{format_string}' size {expected_size}"
            )
