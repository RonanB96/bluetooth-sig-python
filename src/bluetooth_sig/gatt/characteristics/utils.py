"""Utility classes for GATT characteristic parsing and encoding.

This module provides organized utility classes that characteristics can import
and use as needed, maintaining logical grouping of functionality while avoiding
multiple inheritance complexity.
"""

from __future__ import annotations

import math
import struct
from enum import IntEnum
from typing import Any


class DataParser:
    """Utility class for basic data type parsing and encoding."""

    @staticmethod
    def parse_uint8(data: bytearray, offset: int = 0) -> int:
        """Parse unsigned 8-bit integer."""
        if len(data) < offset + 1:
            raise ValueError(f"Insufficient data for uint8 at offset {offset}")
        return data[offset]

    @staticmethod
    def parse_uint16(data: bytearray, offset: int = 0) -> int:
        """Parse unsigned 16-bit integer (little-endian)."""
        if len(data) < offset + 2:
            raise ValueError(f"Insufficient data for uint16 at offset {offset}")
        return int.from_bytes(
            data[offset : offset + 2], byteorder="little", signed=False
        )

    @staticmethod
    def parse_uint32(data: bytearray, offset: int = 0) -> int:
        """Parse unsigned 32-bit integer (little-endian)."""
        if len(data) < offset + 4:
            raise ValueError(f"Insufficient data for uint32 at offset {offset}")
        return int.from_bytes(
            data[offset : offset + 4], byteorder="little", signed=False
        )

    @staticmethod
    def parse_sint16(data: bytearray, offset: int = 0) -> int:
        """Parse signed 16-bit integer (little-endian)."""
        if len(data) < offset + 2:
            raise ValueError(f"Insufficient data for sint16 at offset {offset}")
        return int.from_bytes(
            data[offset : offset + 2], byteorder="little", signed=True
        )

    @staticmethod
    def parse_sint32(data: bytearray, offset: int = 0) -> int:
        """Parse signed 32-bit integer (little-endian)."""
        if len(data) < offset + 4:
            raise ValueError(f"Insufficient data for sint32 at offset {offset}")
        return int.from_bytes(
            data[offset : offset + 4], byteorder="little", signed=True
        )

    @staticmethod
    def parse_float32(data: bytearray, offset: int = 0) -> float:
        """Parse IEEE-754 32-bit float (little-endian)."""
        if len(data) < offset + 4:
            raise ValueError(f"Insufficient data for float32 at offset {offset}")
        return struct.unpack("<f", data[offset : offset + 4])[0]

    @staticmethod
    def parse_float64(data: bytearray, offset: int = 0) -> float:
        """Parse IEEE-754 64-bit double (little-endian)."""
        if len(data) < offset + 8:
            raise ValueError(f"Insufficient data for float64 at offset {offset}")
        return struct.unpack("<d", data[offset : offset + 8])[0]

    @staticmethod
    def parse_utf8_string(data: bytearray) -> str:
        """Parse UTF-8 string from bytearray with null termination handling."""
        return data.decode("utf-8", errors="replace").rstrip("\x00")

    @staticmethod
    def encode_uint8(value: int) -> bytearray:
        """Encode unsigned 8-bit integer."""
        if not 0 <= value <= 255:
            raise ValueError(f"Value {value} out of range for uint8 (0-255)")
        return bytearray([value])

    @staticmethod
    def encode_uint16(value: int) -> bytearray:
        """Encode unsigned 16-bit integer (little-endian)."""
        if not 0 <= value <= 65535:
            raise ValueError(f"Value {value} out of range for uint16 (0-65535)")
        return bytearray(value.to_bytes(2, byteorder="little", signed=False))

    @staticmethod
    def encode_uint32(value: int) -> bytearray:
        """Encode unsigned 32-bit integer (little-endian)."""
        if not 0 <= value <= 4294967295:
            raise ValueError(f"Value {value} out of range for uint32 (0-4294967295)")
        return bytearray(value.to_bytes(4, byteorder="little", signed=False))

    @staticmethod
    def encode_sint16(value: int) -> bytearray:
        """Encode signed 16-bit integer (little-endian)."""
        if not -32768 <= value <= 32767:
            raise ValueError(f"Value {value} out of range for sint16 (-32768 to 32767)")
        return bytearray(value.to_bytes(2, byteorder="little", signed=True))

    @staticmethod
    def encode_sint32(value: int) -> bytearray:
        """Encode signed 32-bit integer (little-endian)."""
        if not -2147483648 <= value <= 2147483647:
            raise ValueError(
                f"Value {value} out of range for sint32 (-2147483648 to 2147483647)"
            )
        return bytearray(value.to_bytes(4, byteorder="little", signed=True))

    @staticmethod
    def encode_float32(value: float) -> bytearray:
        """Encode IEEE-754 32-bit float (little-endian)."""
        return bytearray(struct.pack("<f", value))

    @staticmethod
    def encode_float64(value: float) -> bytearray:
        """Encode IEEE-754 64-bit double (little-endian)."""
        return bytearray(struct.pack("<d", value))


class IEEE11073Parser:
    """Utility class for IEEE-11073 medical device format support."""

    @staticmethod
    def parse_sfloat(sfloat_val: int) -> float:
        """Convert IEEE-11073 16-bit SFLOAT to Python float."""
        if sfloat_val == 0x07FF:  # NaN
            return float("nan")
        if sfloat_val == 0x0800:  # NRes (Not a valid result)
            return float("nan")
        if sfloat_val == 0x07FE:  # +INFINITY
            return float("inf")
        if sfloat_val == 0x0802:  # -INFINITY
            return float("-inf")

        # Extract mantissa and exponent
        mantissa = sfloat_val & 0x0FFF
        exponent = (sfloat_val >> 12) & 0x0F

        # Handle negative mantissa
        if mantissa & 0x0800:
            mantissa = mantissa - 0x1000

        # Handle negative exponent
        if exponent & 0x08:
            exponent = exponent - 0x10

        return mantissa * (10**exponent)

    @staticmethod
    def encode_sfloat(value: float) -> bytearray:
        """Encode Python float to IEEE-11073 16-bit SFLOAT."""
        if math.isnan(value):
            return bytearray([0xFF, 0x07])  # NaN
        if math.isinf(value):
            if value > 0:
                return bytearray([0xFE, 0x07])  # +INFINITY
            return bytearray([0x02, 0x08])  # -INFINITY

        # Find appropriate exponent and mantissa
        if value == 0:
            return bytearray([0x00, 0x00])

        # Determine sign
        sign = -1 if value < 0 else 1
        abs_value = abs(value)

        # Find exponent
        exponent = 0
        mantissa = abs_value

        # Scale to get mantissa in range
        while mantissa >= 2048 and exponent < 7:  # Max mantissa is 2047
            mantissa /= 10
            exponent += 1

        while mantissa < 204.8 and exponent > -8:  # Min mantissa for precision
            mantissa *= 10
            exponent -= 1

        # Round mantissa to integer
        mantissa = round(mantissa) * sign

        # Clamp values to valid ranges
        if mantissa > 2047:
            mantissa = 2047
        elif mantissa < -2048:
            mantissa = -2048

        if exponent > 7:
            exponent = 7
        elif exponent < -8:
            exponent = -8

        # Encode as 16-bit value
        if mantissa < 0:
            mantissa += 4096  # Convert to unsigned representation

        if exponent < 0:
            exponent += 16  # Convert to unsigned representation

        sfloat_val = (exponent << 12) | (mantissa & 0x0FFF)
        return bytearray(sfloat_val.to_bytes(2, byteorder="little", signed=False))

    @staticmethod
    def parse_timestamp(data: bytearray, offset: int) -> dict[str, int]:
        """Parse IEEE-11073 timestamp format (7 bytes)."""
        if len(data) < offset + 7:
            raise ValueError("Not enough data for timestamp parsing")

        timestamp_data = data[offset : offset + 7]
        year, month, day, hours, minutes, seconds = struct.unpack(
            "<HBBBBB", timestamp_data
        )
        return {
            "year": year,
            "month": month,
            "day": day,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
        }

    @staticmethod
    def encode_timestamp(timestamp: dict[str, int]) -> bytearray:
        """Encode timestamp to IEEE-11073 7-byte format."""
        required_keys = {"year", "month", "day", "hours", "minutes", "seconds"}
        if not all(key in timestamp for key in required_keys):
            raise ValueError(f"Timestamp must contain all keys: {required_keys}")

        # Validate ranges
        if not 1582 <= timestamp["year"] <= 9999:
            raise ValueError(f"Year {timestamp['year']} out of range (1582-9999)")
        if not 1 <= timestamp["month"] <= 12:
            raise ValueError(f"Month {timestamp['month']} out of range (1-12)")
        if not 1 <= timestamp["day"] <= 31:
            raise ValueError(f"Day {timestamp['day']} out of range (1-31)")
        if not 0 <= timestamp["hours"] <= 23:
            raise ValueError(f"Hours {timestamp['hours']} out of range (0-23)")
        if not 0 <= timestamp["minutes"] <= 59:
            raise ValueError(f"Minutes {timestamp['minutes']} out of range (0-59)")
        if not 0 <= timestamp["seconds"] <= 59:
            raise ValueError(f"Seconds {timestamp['seconds']} out of range (0-59)")

        return bytearray(
            struct.pack(
                "<HBBBBB",
                timestamp["year"],
                timestamp["month"],
                timestamp["day"],
                timestamp["hours"],
                timestamp["minutes"],
                timestamp["seconds"],
            )
        )


class BitFieldUtils:
    """Utility class for bit field manipulation and flag handling."""

    @staticmethod
    def extract_bit_field(value: int, start_bit: int, num_bits: int) -> int:
        """Extract a bit field from an integer value."""
        if num_bits <= 0 or start_bit < 0:
            raise ValueError("Invalid bit field parameters")
        mask = (1 << num_bits) - 1
        return (value >> start_bit) & mask

    @staticmethod
    def set_bit_field(
        value: int, field_value: int, start_bit: int, num_bits: int
    ) -> int:
        """Set a bit field in an integer value."""
        if num_bits <= 0 or start_bit < 0:
            raise ValueError("Invalid bit field parameters")
        mask = (1 << num_bits) - 1
        if field_value > mask:
            raise ValueError(
                f"Field value {field_value} exceeds {num_bits}-bit capacity"
            )
        # Clear the field and set new value
        value &= ~(mask << start_bit)
        value |= (field_value & mask) << start_bit
        return value

    @staticmethod
    def parse_flags(value: int, flag_names: list[str]) -> dict[str, bool]:
        """Parse bit flags into a dictionary."""
        return {name: bool(value & (1 << i)) for i, name in enumerate(flag_names)}

    @staticmethod
    def encode_flags(flags: dict[str, bool], flag_positions: dict[str, int]) -> int:
        """Encode dictionary of flags into an integer."""
        result = 0
        for flag_name, is_set in flags.items():
            if is_set and flag_name in flag_positions:
                result |= 1 << flag_positions[flag_name]
        return result


class DataValidator:
    """Utility class for data validation and integrity checking."""

    @staticmethod
    def validate_data_length(
        data: bytearray, expected_min: int, expected_max: int | None = None
    ) -> None:
        """Validate data length against expected range."""
        length = len(data)
        if length < expected_min:
            raise ValueError(
                f"Data too short: {length} bytes, expected at least {expected_min}"
            )
        if expected_max is not None and length > expected_max:
            raise ValueError(
                f"Data too long: {length} bytes, expected at most {expected_max}"
            )

    @staticmethod
    def validate_range(
        value: int | float, min_val: int | float, max_val: int | float
    ) -> None:
        """Validate that a value is within the specified range."""
        if not min_val <= value <= max_val:
            raise ValueError(f"Value {value} out of range [{min_val}, {max_val}]")

    @staticmethod
    def validate_enum_value(value: int, enum_class: type[IntEnum]) -> None:
        """Validate that a value is a valid member of an IntEnum."""
        try:
            enum_class(value)
        except ValueError as e:
            valid_values = [member.value for member in enum_class]
            raise ValueError(
                f"Invalid {enum_class.__name__} value {value}. Valid values: {valid_values}"
            ) from e


class DebugUtils:
    """Utility class for debugging and testing support."""

    @staticmethod
    def format_hex_dump(data: bytearray) -> str:
        """Format data as a hex dump for debugging."""
        return " ".join(f"{byte:02X}" for byte in data)

    @staticmethod
    def validate_round_trip(characteristic: Any, original_data: bytearray) -> bool:
        """Validate that parse/encode operations preserve data integrity."""
        try:
            parsed = characteristic.parse_value(original_data)
            encoded = characteristic.encode_value(parsed)
            return original_data == encoded
        except Exception:  # pylint: disable=broad-except
            return False
