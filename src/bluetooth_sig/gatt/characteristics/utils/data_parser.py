"""Data parsing utilities for basic data types."""

from __future__ import annotations

import struct
from typing import Literal

from ...constants import (
    SINT8_MAX,
    SINT8_MIN,
    SINT16_MAX,
    SINT16_MIN,
    SINT24_MAX,
    SINT24_MIN,
    SINT32_MAX,
    SINT32_MIN,
    UINT8_MAX,
    UINT16_MAX,
    UINT24_MAX,
    UINT32_MAX,
)
from ...exceptions import InsufficientDataError, ValueRangeError

# Sign threshold for int8 values (values >= 128 are negative when signed)
_INT8_SIGN_THRESHOLD = 128


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
        if signed and value >= _INT8_SIGN_THRESHOLD:
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
        return int.from_bytes(data[offset : offset + 2], byteorder=endian, signed=signed)

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
        return int.from_bytes(data[offset : offset + 4], byteorder=endian, signed=signed)

    @staticmethod
    def parse_int24(
        data: bytes | bytearray,
        offset: int = 0,
        signed: bool = False,
        endian: Literal["little", "big"] = "little",
    ) -> int:
        """Parse 24-bit integer with configurable endianness and signed interpretation."""
        if len(data) < offset + 3:
            raise InsufficientDataError("int24", data[offset:], 3)
        return int.from_bytes(data[offset : offset + 3], byteorder=endian, signed=signed)

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
    def parse_variable_length(data: bytes | bytearray, min_length: int, max_length: int) -> bytes:
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
        elif not 0 <= value <= UINT8_MAX:
            raise ValueRangeError("uint8", value, 0, UINT8_MAX)
        return bytearray(value.to_bytes(1, byteorder="little", signed=signed))

    @staticmethod
    def encode_int16(value: int, signed: bool = False, endian: Literal["little", "big"] = "little") -> bytearray:
        """Encode 16-bit integer with configurable endianness and signed/unsigned validation."""
        if signed:
            if not SINT16_MIN <= value <= SINT16_MAX:
                raise ValueRangeError("sint16", value, SINT16_MIN, SINT16_MAX)
        elif not 0 <= value <= UINT16_MAX:
            raise ValueRangeError("uint16", value, 0, UINT16_MAX)
        return bytearray(value.to_bytes(2, byteorder=endian, signed=signed))

    @staticmethod
    def encode_int32(value: int, signed: bool = False, endian: Literal["little", "big"] = "little") -> bytearray:
        """Encode 32-bit integer with configurable endianness and signed/unsigned validation."""
        if signed:
            if not SINT32_MIN <= value <= SINT32_MAX:
                raise ValueRangeError("sint32", value, SINT32_MIN, SINT32_MAX)
        elif not 0 <= value <= UINT32_MAX:
            raise ValueRangeError("uint32", value, 0, UINT32_MAX)
        return bytearray(value.to_bytes(4, byteorder=endian, signed=signed))

    @staticmethod
    def encode_int24(value: int, signed: bool = False, endian: Literal["little", "big"] = "little") -> bytearray:
        """Encode 24-bit integer with configurable endianness and signed/unsigned validation."""
        if signed:
            if not SINT24_MIN <= value <= SINT24_MAX:
                raise ValueRangeError("sint24", value, SINT24_MIN, SINT24_MAX)
        elif not 0 <= value <= UINT24_MAX:
            raise ValueRangeError("uint24", value, 0, UINT24_MAX)
        return bytearray(value.to_bytes(3, byteorder=endian, signed=signed))

    @staticmethod
    def encode_float32(value: float) -> bytearray:
        """Encode IEEE-754 32-bit float (little-endian)."""
        return bytearray(struct.pack("<f", value))

    @staticmethod
    def encode_float64(value: float) -> bytearray:
        """Encode IEEE-754 64-bit double (little-endian)."""
        return bytearray(struct.pack("<d", value))
