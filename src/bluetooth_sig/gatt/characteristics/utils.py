"""Utility classes for GATT characteristic parsing and encoding.

This module provides organized utility classes that characteristics can import
and use as needed, maintaining logical grouping of functionality while avoiding
multiple inheritance complexity.
"""

from __future__ import annotations

import math
import struct
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import Any, Literal

from ..constants import (
    IEEE11073_NAN,
    IEEE11073_NEGATIVE_INFINITY,
    IEEE11073_NRES,
    IEEE11073_POSITIVE_INFINITY,
    MAX_CONCENTRATION_PPM,
    MAX_POWER_WATTS,
    MAX_TEMPERATURE_CELSIUS,
    SINT8_MAX,
    SINT8_MIN,
    SINT16_MAX,
    SINT16_MIN,
    SINT32_MAX,
    SINT32_MIN,
    UINT8_MAX,
    UINT16_MAX,
    UINT32_MAX,
)
from ..exceptions import (
    DataValidationError,
    EnumValueError,
    InsufficientDataError,
    TypeMismatchError,
    ValueRangeError,
)


@dataclass
class FlagInfo:
    """Bit flag information."""

    flags: dict[str, bool]


class DataParser:
    """Utility class for basic data type parsing and encoding."""

    @staticmethod
    def parse_int8(
        data: bytes | bytearray,
        offset: int = 0,
        signed: bool = False,
    ) -> int:
        """Parse 8-bit integer with optional signed interpretation."""
        if len(data) < offset + 1:
            raise InsufficientDataError("int8", data[offset:], 1)
        value = data[offset]
        if signed and value >= 128:
            return value - 256
        return value

    @staticmethod
    def parse_int16(
        data: bytes | bytearray,
        offset: int = 0,
        signed: bool = False,
        endian: Literal["little", "big"] = "little",
    ) -> int:
        """Parse 16-bit integer with configurable endianness and signed interpretation."""
        if len(data) < offset + 2:
            raise InsufficientDataError("int16", data[offset:], 2)
        return int.from_bytes(
            data[offset : offset + 2], byteorder=endian, signed=signed
        )

    @staticmethod
    def parse_int32(
        data: bytes | bytearray,
        offset: int = 0,
        signed: bool = False,
        endian: Literal["little", "big"] = "little",
    ) -> int:
        """Parse 32-bit integer with configurable endianness and signed interpretation."""
        if len(data) < offset + 4:
            raise InsufficientDataError("int32", data[offset:], 4)
        return int.from_bytes(
            data[offset : offset + 4], byteorder=endian, signed=signed
        )

    @staticmethod
    def parse_float32(data: bytearray, offset: int = 0) -> float:
        """Parse IEEE-754 32-bit float (little-endian)."""
        if len(data) < offset + 4:
            raise InsufficientDataError("float32", data[offset:], 4)
        return float(struct.unpack("<f", data[offset : offset + 4])[0])

    @staticmethod
    def parse_float64(data: bytearray, offset: int = 0) -> float:
        """Parse IEEE-754 64-bit double (little-endian)."""
        if len(data) < offset + 8:
            raise InsufficientDataError("float64", data[offset:], 8)
        return float(struct.unpack("<d", data[offset : offset + 8])[0])

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
    def encode_int8(value: int, signed: bool = False) -> bytearray:
        """Encode 8-bit integer with signed/unsigned validation."""
        if signed:
            if not SINT8_MIN <= value <= SINT8_MAX:
                raise ValueRangeError("sint8", value, SINT8_MIN, SINT8_MAX)
        else:
            if not 0 <= value <= UINT8_MAX:
                raise ValueRangeError("uint8", value, 0, UINT8_MAX)
        return bytearray(value.to_bytes(1, byteorder="little", signed=signed))

    @staticmethod
    def encode_int16(
        value: int, signed: bool = False, endian: Literal["little", "big"] = "little"
    ) -> bytearray:
        """Encode 16-bit integer with configurable endianness and signed/unsigned validation."""
        if signed:
            if not SINT16_MIN <= value <= SINT16_MAX:
                raise ValueRangeError("sint16", value, SINT16_MIN, SINT16_MAX)
        else:
            if not 0 <= value <= UINT16_MAX:
                raise ValueRangeError("uint16", value, 0, UINT16_MAX)
        return bytearray(value.to_bytes(2, byteorder=endian, signed=signed))

    @staticmethod
    def encode_int32(
        value: int, signed: bool = False, endian: Literal["little", "big"] = "little"
    ) -> bytearray:
        """Encode 32-bit integer with configurable endianness and signed/unsigned validation."""
        if signed:
            if not SINT32_MIN <= value <= SINT32_MAX:
                raise ValueRangeError("sint32", value, SINT32_MIN, SINT32_MAX)
        else:
            if not 0 <= value <= UINT32_MAX:
                raise ValueRangeError("uint32", value, 0, UINT32_MAX)
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
            raise InsufficientDataError("IEEE 11073 SFLOAT", data[offset:], 2)
        raw_value = int.from_bytes(data[offset : offset + 2], byteorder="little")

        # Handle special values
        if raw_value == IEEE11073_NAN:
            return float("nan")  # NaN
        if raw_value == IEEE11073_NRES:
            return float("nan")  # NRes (Not a valid result)
        if raw_value == IEEE11073_POSITIVE_INFINITY:
            return float("inf")  # +INFINITY
        if raw_value == IEEE11073_NEGATIVE_INFINITY:
            return float("-inf")  # -INFINITY

        # Extract mantissa and exponent
        mantissa = raw_value & 0x0FFF
        if mantissa >= 0x0800:  # Negative mantissa
            mantissa = mantissa - 0x1000

        exponent = (raw_value >> 12) & 0x0F
        if exponent >= 0x08:  # Negative exponent
            exponent = exponent - 0x10

        return float(mantissa * (10.0**exponent))

    @staticmethod
    def parse_float32(data: bytes | bytearray, offset: int = 0) -> float:
        """Parse IEEE 11073 32-bit FLOAT."""
        if len(data) < offset + 4:
            raise InsufficientDataError("IEEE 11073 FLOAT32", data[offset:], 4)

        raw_value = int.from_bytes(data[offset : offset + 4], byteorder="little")

        # Handle special values (similar to SFLOAT but 32-bit)
        if raw_value == 0x007FFFFF:
            return float("nan")
        if raw_value == 0x00800000:
            return float("inf")
        if raw_value == 0x00800001:
            return float("-inf")
        if raw_value == 0x00800002:
            return float("nan")  # NRes (Not a valid result)

        # Extract mantissa (24-bit) and exponent (8-bit)
        mantissa = raw_value & 0x00FFFFFF
        if mantissa >= 0x00800000:  # Negative mantissa
            mantissa = mantissa - 0x01000000

        exponent = (raw_value >> 24) & 0xFF
        if exponent >= 0x80:  # Negative exponent
            exponent = exponent - 0x100

        return float(mantissa * (10**exponent))

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
    def parse_timestamp(data: bytearray, offset: int) -> datetime:
        """Parse IEEE-11073 timestamp format (7 bytes)."""
        if len(data) < offset + 7:
            raise InsufficientDataError("IEEE 11073 timestamp", data[offset:], 7)

        timestamp_data = data[offset : offset + 7]
        year, month, day, hours, minutes, seconds = struct.unpack(
            "<HBBBBB", timestamp_data
        )
        return datetime(year, month, day, hours, minutes, seconds)

    @staticmethod
    def encode_timestamp(timestamp: datetime) -> bytearray:
        """Encode timestamp to IEEE-11073 7-byte format."""
        # Validate ranges
        if not 1582 <= timestamp.year <= 9999:
            raise ValueRangeError("year", timestamp.year, 1582, 9999)
        if not 1 <= timestamp.month <= 12:
            raise ValueRangeError("month", timestamp.month, 1, 12)
        if not 1 <= timestamp.day <= 31:
            raise ValueRangeError("day", timestamp.day, 1, 31)
        if not 0 <= timestamp.hour <= 23:
            raise ValueRangeError("hour", timestamp.hour, 0, 23)
        if not 0 <= timestamp.minute <= 59:
            raise ValueRangeError("minute", timestamp.minute, 0, 59)
        if not 0 <= timestamp.second <= 59:
            raise ValueRangeError("second", timestamp.second, 0, 59)

        return bytearray(
            struct.pack(
                "<HBBBBB",
                timestamp.year,
                timestamp.month,
                timestamp.day,
                timestamp.hour,
                timestamp.minute,
                timestamp.second,
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
    def parse_flags(value: int, flag_names: list[str]) -> FlagInfo:
        """Parse bit flags into a FlagInfo object."""
        flags = {name: bool(value & (1 << i)) for i, name in enumerate(flag_names)}
        return FlagInfo(flags=flags)

    @staticmethod
    def encode_flags(flag_info: FlagInfo, flag_positions: dict[str, int]) -> int:
        """Encode FlagInfo object into an integer."""
        result = 0
        for flag_name, is_set in flag_info.flags.items():
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
            raise InsufficientDataError("data", data, expected_min)
        if expected_max is not None and length > expected_max:
            raise DataValidationError(
                "data_length", length, f"at most {expected_max} bytes"
            )

    @staticmethod
    def validate_range(
        value: int | float, min_val: int | float, max_val: int | float
    ) -> None:
        """Validate that a value is within the specified range."""
        if not min_val <= value <= max_val:
            raise ValueRangeError("value", value, min_val, max_val)

    @staticmethod
    def validate_enum_value(value: int, enum_class: type[IntEnum]) -> None:
        """Validate that a value is a valid member of an IntEnum."""
        try:
            enum_class(value)
        except ValueError as e:
            valid_values = [member.value for member in enum_class]
            raise EnumValueError(
                enum_class.__name__, value, enum_class, valid_values
            ) from e

    @staticmethod
    def validate_concentration_range(
        value: float, max_ppm: float = MAX_CONCENTRATION_PPM
    ) -> None:
        """Validate concentration value is in acceptable range."""
        if not isinstance(value, (int, float)):
            raise TypeMismatchError("concentration", value, float)
        if value < 0:
            raise ValueRangeError("concentration", value, 0, max_ppm)
        if value > max_ppm:
            raise ValueRangeError("concentration", value, 0, max_ppm)

    @staticmethod
    def validate_temperature_range(
        value: float,
        min_celsius: float = -273.15,
        max_celsius: float = MAX_TEMPERATURE_CELSIUS,
    ) -> None:
        """Validate temperature is in physically reasonable range."""
        if not isinstance(value, (int, float)):
            raise TypeMismatchError("temperature", value, float)
        if value < min_celsius:
            raise ValueRangeError("temperature", value, min_celsius, max_celsius)
        if value > max_celsius:
            raise ValueRangeError("temperature", value, min_celsius, max_celsius)

    @staticmethod
    def validate_percentage(value: int | float, allow_over_100: bool = False) -> None:
        """Validate percentage value (0-100% or 0-200% for some characteristics)."""
        if not isinstance(value, (int, float)):
            raise TypeMismatchError("percentage", value, float)
        max_value = 200 if allow_over_100 else 100
        if value < 0 or value > max_value:
            raise ValueRangeError("percentage", value, 0, max_value)

    @staticmethod
    def validate_power_range(
        value: int | float, max_watts: float = MAX_POWER_WATTS
    ) -> None:
        """Validate power measurement range."""
        if not isinstance(value, (int, float)):
            raise TypeMismatchError("power", value, float)
        if value < 0 or value > max_watts:
            raise ValueRangeError("power", value, 0, max_watts)


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
            return bool(original_data == encoded)
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
        expected_size = struct.calcsize(format_string)
        actual_size = len(data)
        if actual_size != expected_size:
            raise ValueError(
                f"Data size {actual_size} doesn't match format '{format_string}' size {expected_size}"
            )
