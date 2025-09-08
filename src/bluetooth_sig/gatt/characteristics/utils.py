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
    def parse_int8(
        data: bytes | bytearray,
        offset: int = 0,
        signed: bool = False,
        endian: str = "little",  # pylint: disable=unused-argument # Reserved for future use
    ) -> int:
        """Parse 8-bit integer with optional signed interpretation."""
        if len(data) < offset + 1:
            raise ValueError(f"Insufficient data for int8 at offset {offset}")
        value = data[offset]
        if signed and value >= 128:
            return value - 256
        return value

    @staticmethod
    def parse_int16(
        data: bytes | bytearray,
        offset: int = 0,
        signed: bool = False,
        endian: str = "little",
    ) -> int:
        """Parse 16-bit integer with configurable endianness and signed interpretation."""
        if len(data) < offset + 2:
            raise ValueError(f"Insufficient data for int16 at offset {offset}")
        return int.from_bytes(
            data[offset : offset + 2], byteorder=endian, signed=signed
        )

    @staticmethod
    def parse_int32(
        data: bytes | bytearray,
        offset: int = 0,
        signed: bool = False,
        endian: str = "little",
    ) -> int:
        """Parse 32-bit integer with configurable endianness and signed interpretation."""
        if len(data) < offset + 4:
            raise ValueError(f"Insufficient data for int32 at offset {offset}")
        return int.from_bytes(
            data[offset : offset + 4], byteorder=endian, signed=signed
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
    def parse_variable_length(
        data: bytes | bytearray, min_length: int, max_length: int
    ) -> bytes:
        """Parse variable length data with validation."""
        length = len(data)
        if length < min_length:
            raise ValueError(f"Data too short: {length} < {min_length}")
        if length > max_length:
            raise ValueError(f"Data too long: {length} > {max_length}")
        return bytes(data)

    @staticmethod
    def encode_int8(
        value: int, signed: bool = False, endian: str = "little"
    ) -> bytearray:
        """Encode 8-bit integer with signed/unsigned validation."""
        if signed:
            if not -128 <= value <= 127:
                raise ValueError(f"Value {value} out of sint8 range (-128 to 127)")
        else:
            if not 0 <= value <= 255:
                raise ValueError(f"Value {value} out of uint8 range (0-255)")
        return bytearray(value.to_bytes(1, byteorder=endian, signed=signed))

    @staticmethod
    def encode_int16(
        value: int, signed: bool = False, endian: str = "little"
    ) -> bytearray:
        """Encode 16-bit integer with configurable endianness and signed/unsigned validation."""
        if signed:
            if not -32768 <= value <= 32767:
                raise ValueError(f"Value {value} out of sint16 range (-32768 to 32767)")
        else:
            if not 0 <= value <= 65535:
                raise ValueError(f"Value {value} out of uint16 range (0-65535)")
        return bytearray(value.to_bytes(2, byteorder=endian, signed=signed))

    @staticmethod
    def encode_int32(
        value: int, signed: bool = False, endian: str = "little"
    ) -> bytearray:
        """Encode 32-bit integer with configurable endianness and signed/unsigned validation."""
        if signed:
            if not -2147483648 <= value <= 2147483647:
                raise ValueError(f"Value {value} out of sint32 range")
        else:
            if not 0 <= value <= 4294967295:
                raise ValueError(f"Value {value} out of uint32 range")
        return bytearray(value.to_bytes(4, byteorder=endian, signed=signed))

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
    def parse_sfloat(data: bytes | bytearray, offset: int = 0) -> float:
        """Parse IEEE 11073 16-bit SFLOAT.

        Args:
            data: Raw bytes/bytearray
            offset: Offset in the data
        """
        if len(data) < offset + 2:
            raise ValueError(f"Insufficient data for SFLOAT at offset {offset}")
        raw_value = int.from_bytes(data[offset : offset + 2], byteorder="little")

        # Handle special values
        if raw_value == 0x07FF:
            return float("nan")  # NaN
        if raw_value == 0x0800:
            return float("nan")  # NRes (Not a valid result)
        if raw_value == 0x07FE:
            return float("inf")  # +INFINITY
        if raw_value == 0x0802:
            return float("-inf")  # -INFINITY

        # Extract mantissa and exponent
        mantissa = raw_value & 0x0FFF
        if mantissa >= 0x0800:  # Negative mantissa
            mantissa = mantissa - 0x1000

        exponent = (raw_value >> 12) & 0x0F
        if exponent >= 0x08:  # Negative exponent
            exponent = exponent - 0x10

        return mantissa * (10**exponent)

    @staticmethod
    def parse_float32(data: bytes | bytearray, offset: int = 0) -> float:
        """Parse IEEE 11073 32-bit FLOAT."""
        if len(data) < offset + 4:
            raise ValueError(f"Insufficient data for FLOAT32 at offset {offset}")

        raw_value = int.from_bytes(data[offset : offset + 4], byteorder="little")

        # Handle special values (similar to SFLOAT but 32-bit)
        if raw_value == 0x007FFFFF:
            return float("nan")
        if raw_value == 0x00800000:
            return float("inf")
        if raw_value == 0x00800001:
            return float("-inf")
        if raw_value == 0x00800002:
            return None  # NRes

        # Extract mantissa (24-bit) and exponent (8-bit)
        mantissa = raw_value & 0x00FFFFFF
        if mantissa >= 0x00800000:  # Negative mantissa
            mantissa = mantissa - 0x01000000

        exponent = (raw_value >> 24) & 0xFF
        if exponent >= 0x80:  # Negative exponent
            exponent = exponent - 0x100

        return mantissa * (10**exponent)

    @staticmethod
    def encode_sfloat(value: float) -> bytearray:
        """Encode float to IEEE 11073 16-bit SFLOAT."""

        if math.isnan(value):
            return bytearray([0xFF, 0x07])  # NaN
        if math.isinf(value):
            if value > 0:
                return bytearray([0x00, 0x08])  # +INFINITY
            return bytearray([0x01, 0x08])  # -INFINITY

        # Find best exponent and mantissa representation
        exponent = 0
        mantissa = value

        while abs(mantissa) >= 2048 and exponent < 7:
            mantissa /= 10
            exponent += 1

        while abs(mantissa) < 1 and mantissa != 0 and exponent > -8:
            mantissa *= 10
            exponent -= 1

        mantissa_int = int(round(mantissa))

        # Pack into 16-bit value
        if exponent < 0:
            exponent = exponent + 16
        if mantissa_int < 0:
            mantissa_int = mantissa_int + 4096

        raw_value = (exponent << 12) | (mantissa_int & 0x0FFF)
        return bytearray(raw_value.to_bytes(2, byteorder="little"))

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

    @staticmethod
    def validate_concentration_range(value: float, max_ppm: float = 65535.0) -> None:
        """Validate concentration value is in acceptable range."""
        if not isinstance(value, (int, float)):
            raise TypeError(f"Concentration must be numeric, got {type(value)}")
        if value < 0:
            raise ValueError(f"Concentration cannot be negative: {value}")
        if value > max_ppm:
            raise ValueError(f"Concentration {value} exceeds maximum {max_ppm} ppm")

    @staticmethod
    def validate_temperature_range(
        value: float, min_celsius: float = -273.15, max_celsius: float = 1000.0
    ) -> None:
        """Validate temperature is in physically reasonable range."""
        if not isinstance(value, (int, float)):
            raise TypeError(f"Temperature must be numeric, got {type(value)}")
        if value < min_celsius:
            raise ValueError(f"Temperature {value}°C below absolute zero")
        if value > max_celsius:
            raise ValueError(f"Temperature {value}°C exceeds maximum {max_celsius}°C")

    @staticmethod
    def validate_percentage(value: int | float, allow_over_100: bool = False) -> None:
        """Validate percentage value (0-100% or 0-200% for some characteristics)."""
        if not isinstance(value, (int, float)):
            raise TypeError(f"Percentage must be numeric, got {type(value)}")
        if value < 0:
            raise ValueError(f"Percentage cannot be negative: {value}")
        max_value = 200 if allow_over_100 else 100
        if value > max_value:
            raise ValueError(f"Percentage {value}% exceeds maximum {max_value}%")

    @staticmethod
    def validate_power_range(value: int | float, max_watts: float = 65535.0) -> None:
        """Validate power measurement range."""
        if not isinstance(value, (int, float)):
            raise TypeError(f"Power must be numeric, got {type(value)}")
        if value < 0:
            raise ValueError(f"Power cannot be negative: {value}")
        if value > max_watts:
            raise ValueError(f"Power {value}W exceeds maximum {max_watts}W")


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

    @staticmethod
    def format_measurement_value(
        value: Any, unit: str | None = None, precision: int = 2
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
        return separator.join(f"{byte:02X}" for byte in data)

    @staticmethod
    def format_binary_flags(value: int, bit_names: list[str]) -> str:
        """Format integer as binary flags with names."""
        flags = []
        for i, name in enumerate(bit_names):
            if value & (1 << i):
                flags.append(name)
        return ", ".join(flags) if flags else "None"

    @staticmethod
    def validate_struct_format(data: bytes | bytearray, format_string: str) -> None:
        """Validate data length matches struct format requirements."""
        import struct as struct_module  # pylint: disable=import-outside-toplevel # Used only for validation

        expected_size = struct_module.calcsize(format_string)
        actual_size = len(data)
        if actual_size != expected_size:
            raise ValueError(
                f"Data size {actual_size} doesn't match format '{format_string}' size {expected_size}"
            )
