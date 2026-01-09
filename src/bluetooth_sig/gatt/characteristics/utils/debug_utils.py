"""Debug utility methods for characteristic parsing."""

from __future__ import annotations

import struct
from typing import Any

from bluetooth_sig.types.data_types import ParseFieldError
from bluetooth_sig.types.protocols import CharacteristicProtocol

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
    def validate_round_trip(characteristic: CharacteristicProtocol, original_data: bytearray) -> bool:
        """Validate that parse/encode operations preserve data integrity."""
        try:
            parsed = characteristic.parse_value(original_data)
            encoded = characteristic.build_value(parsed)
            return bool(original_data == encoded)
        except Exception:  # pylint: disable=broad-except
            return False

    @staticmethod
    def format_measurement_value(
        value: int | float | str | None,
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
            raise ValueError(f"Data size {actual_size} doesn't match format '{format_string}' size {expected_size}")

    @staticmethod
    def format_field_error(error: ParseFieldError, data: bytes | bytearray) -> str:
        """Format a field-level parsing error with context.

        Args:
            error: The ParseFieldError to format
            data: Complete raw data for context

        Returns:
            Formatted error message with hex dump and field context

        """
        parts = [f"Field '{error.field}' failed: {error.reason}"]

        if error.offset is not None:
            parts.append(f"Offset: {error.offset}")

        # Show hex dump of the problematic slice or full data
        if error.raw_slice:
            hex_dump = DebugUtils.format_hex_data(error.raw_slice)
            parts.append(f"Data: [{hex_dump}]")
        elif data:
            # Show context around the error
            if error.offset is not None and error.offset < len(data):
                # Show a few bytes before and after the offset
                start = max(0, error.offset - 2)
                end = min(len(data), error.offset + 3)
                context_slice = data[start:end]
                hex_dump = DebugUtils.format_hex_data(context_slice)
                parts.append(f"Context at offset {start}: [{hex_dump}]")
            else:
                # Show all data if offset not available
                hex_dump = DebugUtils.format_hex_data(data)
                parts.append(f"Full data: [{hex_dump}]")

        return " | ".join(parts)

    @staticmethod
    def format_field_errors(errors: list[Any], data: bytes | bytearray) -> str:
        """Format multiple field errors into a readable message.

        Args:
            errors: List of ParseFieldError objects
            data: Complete raw data for context

        Returns:
            Formatted string with all field errors and context

        """
        if not errors:
            return "No field errors"

        lines = [f"Found {len(errors)} field error(s):"]
        for i, error in enumerate(errors, 1):
            lines.append(f"  {i}. {DebugUtils.format_field_error(error, data)}")

        return "\n".join(lines)

    @staticmethod
    def format_parse_trace(trace: list[str]) -> str:
        """Format parse trace as readable steps.

        Args:
            trace: List of parse trace entries

        Returns:
            Formatted trace string

        """
        if not trace:
            return "No parse trace available"

        lines = ["Parse trace:"]
        for i, step in enumerate(trace, 1):
            lines.append(f"  {i}. {step}")

        return "\n".join(lines)
