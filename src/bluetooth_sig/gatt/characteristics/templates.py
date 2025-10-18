# mypy: warn_unused_ignores=False
"""Coding templates for characteristic composition patterns.

This module provides reusable coding template classes that can be composed into
characteristics via dependency injection. Templates are pure coding strategies
that do NOT inherit from BaseCharacteristic.

All templates follow the CodingTemplate protocol and can be used by both SIG
and custom characteristics through composition.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import msgspec

from ..constants import (
    PERCENTAGE_MAX,
    SINT8_MAX,
    SINT8_MIN,
    SINT16_MAX,
    SINT16_MIN,
    SINT24_MAX,
    SINT24_MIN,
    TEMPERATURE_RESOLUTION,
    UINT8_MAX,
    UINT16_MAX,
    UINT24_MAX,
    UINT32_MAX,
)
from ..context import CharacteristicContext
from .utils import DataParser, IEEE11073Parser

# =============================================================================
# LEVEL 4 BASE CLASS
# =============================================================================


class CodingTemplate(ABC):
    """Abstract base class for coding templates.

    Templates are pure coding utilities that don't inherit from BaseCharacteristic.
    They provide coding strategies that can be injected into characteristics.
    All templates MUST inherit from this base class and implement the required methods.
    """

    @abstractmethod
    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> Any:  # noqa: ANN401  # Returns various types (int, float, str, dataclass)
        """Decode raw bytes to typed value.

        Args:
            data: Raw bytes to parse
            offset: Byte offset to start parsing from
            ctx: Optional context for parsing

        Returns:
            Parsed value of appropriate type (int, float, str, bytes, or custom dataclass)

        """

    @abstractmethod
    def encode_value(self, value: Any) -> bytearray:  # noqa: ANN401  # Accepts various value types (int, float, str, dataclass)
        """Encode typed value to raw bytes.

        Args:
            value: Typed value to encode

        Returns:
            Raw bytes representing the value

        """

    @property
    @abstractmethod
    def data_size(self) -> int:
        """Size of data in bytes that this template handles."""


# =============================================================================
# DATA STRUCTURES
# =============================================================================


class VectorData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """3D vector measurement data."""

    x_axis: float
    y_axis: float
    z_axis: float


class Vector2DData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """2D vector measurement data."""

    x_axis: float
    y_axis: float


# =============================================================================
# BASIC INTEGER TEMPLATES
# =============================================================================


class Uint8Template(CodingTemplate):
    """Template for 8-bit unsigned integer parsing (0-255)."""

    @property
    def data_size(self) -> int:
        """Size: 1 byte."""
        return 1

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> int:
        """Parse 8-bit unsigned integer."""
        if len(data) < offset + 1:
            raise ValueError("Insufficient data for uint8 parsing")
        return DataParser.parse_int8(data, offset, signed=False)

    def encode_value(self, value: int) -> bytearray:
        """Encode uint8 value to bytes."""
        if not 0 <= value <= UINT8_MAX:
            raise ValueError(f"Value {value} out of range for uint8 (0-{UINT8_MAX})")
        return DataParser.encode_int8(value, signed=False)


class Sint8Template(CodingTemplate):
    """Template for 8-bit signed integer parsing (-128 to 127)."""

    @property
    def data_size(self) -> int:
        """Size: 1 byte."""
        return 1

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> int:
        """Parse 8-bit signed integer."""
        if len(data) < offset + 1:
            raise ValueError("Insufficient data for sint8 parsing")
        return DataParser.parse_int8(data, offset, signed=True)

    def encode_value(self, value: int) -> bytearray:
        """Encode sint8 value to bytes."""
        if not SINT8_MIN <= value <= SINT8_MAX:
            raise ValueError(f"Value {value} out of range for sint8 ({SINT8_MIN} to {SINT8_MAX})")
        return DataParser.encode_int8(value, signed=True)


class Uint16Template(CodingTemplate):
    """Template for 16-bit unsigned integer parsing (0-65535)."""

    @property
    def data_size(self) -> int:
        """Size: 2 bytes."""
        return 2

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> int:
        """Parse 16-bit unsigned integer."""
        if len(data) < offset + 2:
            raise ValueError("Insufficient data for uint16 parsing")
        return DataParser.parse_int16(data, offset, signed=False)

    def encode_value(self, value: int) -> bytearray:
        """Encode uint16 value to bytes."""
        if not 0 <= value <= UINT16_MAX:
            raise ValueError(f"Value {value} out of range for uint16 (0-{UINT16_MAX})")
        return DataParser.encode_int16(value, signed=False)


class Sint16Template(CodingTemplate):
    """Template for 16-bit signed integer parsing (-32768 to 32767)."""

    @property
    def data_size(self) -> int:
        """Size: 2 bytes."""
        return 2

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> int:
        """Parse 16-bit signed integer."""
        if len(data) < offset + 2:
            raise ValueError("Insufficient data for sint16 parsing")
        return DataParser.parse_int16(data, offset, signed=True)

    def encode_value(self, value: int) -> bytearray:
        """Encode sint16 value to bytes."""
        if not SINT16_MIN <= value <= SINT16_MAX:
            raise ValueError(f"Value {value} out of range for sint16 ({SINT16_MIN} to {SINT16_MAX})")
        return DataParser.encode_int16(value, signed=True)


class Uint32Template(CodingTemplate):
    """Template for 32-bit unsigned integer parsing."""

    @property
    def data_size(self) -> int:
        """Size: 4 bytes."""
        return 4

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> int:
        """Parse 32-bit unsigned integer."""
        if len(data) < offset + 4:
            raise ValueError("Insufficient data for uint32 parsing")
        return DataParser.parse_int32(data, offset, signed=False)

    def encode_value(self, value: int) -> bytearray:
        """Encode uint32 value to bytes."""
        if not 0 <= value <= UINT32_MAX:
            raise ValueError(f"Value {value} out of range for uint32 (0-{UINT32_MAX})")
        return DataParser.encode_int32(value, signed=False)


# =============================================================================
# SCALED VALUE TEMPLATES
# =============================================================================


class ScaledUint16Template(CodingTemplate):
    """Template for scaled 16-bit unsigned integer with configurable resolution.

    Used for values that need decimal precision encoded as integers.
    Example: Temperature 25.5°C stored as 2550 with scale_factor=0.01
    """

    def __init__(self, scale_factor: float = 0.01) -> None:
        """Initialize with scale factor.

        Args:
            scale_factor: Factor to multiply raw value by (e.g., 0.01 for 2 decimal places)

        """
        self.scale_factor = scale_factor

    @property
    def data_size(self) -> int:
        """Size: 2 bytes."""
        return 2

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> float:
        """Parse scaled 16-bit unsigned integer."""
        if len(data) < offset + 2:
            raise ValueError("Insufficient data for scaled uint16 parsing")
        raw_value = DataParser.parse_int16(data, offset, signed=False)
        return raw_value * self.scale_factor

    def encode_value(self, value: float) -> bytearray:
        """Encode scaled value to bytes."""
        raw_value = int(value / self.scale_factor)
        if not 0 <= raw_value <= UINT16_MAX:
            raise ValueError(f"Scaled value {raw_value} out of range for uint16")
        return DataParser.encode_int16(raw_value, signed=False)


class ScaledSint16Template(CodingTemplate):
    """Template for scaled 16-bit signed integer with configurable resolution.

    Used for signed values that need decimal precision encoded as integers.
    Example: Temperature -10.5°C stored as -1050 with scale_factor=0.01
    """

    def __init__(self, scale_factor: float = 0.01) -> None:
        """Initialize with scale factor.

        Args:
            scale_factor: Factor to multiply raw value by

        """
        self.scale_factor = scale_factor

    @property
    def data_size(self) -> int:
        """Size: 2 bytes."""
        return 2

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> float:
        """Parse scaled 16-bit signed integer."""
        if len(data) < offset + 2:
            raise ValueError("Insufficient data for scaled sint16 parsing")
        raw_value = DataParser.parse_int16(data, offset, signed=True)
        return raw_value * self.scale_factor

    def encode_value(self, value: float) -> bytearray:
        """Encode scaled value to bytes."""
        raw_value = int(value / self.scale_factor)
        if not SINT16_MIN <= raw_value <= SINT16_MAX:
            raise ValueError(f"Scaled value {raw_value} out of range for sint16")
        return DataParser.encode_int16(raw_value, signed=True)


class ScaledUint32Template(CodingTemplate):
    """Template for scaled 32-bit unsigned integer with configurable resolution."""

    def __init__(self, scale_factor: float = 0.1) -> None:
        """Initialize with scale factor.

        Args:
            scale_factor: Factor to multiply raw value by (e.g., 0.1 for 1 decimal place)

        """
        self.scale_factor = scale_factor

    @property
    def data_size(self) -> int:
        """Size: 4 bytes."""
        return 4

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> float:
        """Parse scaled 32-bit unsigned integer."""
        if len(data) < offset + 4:
            raise ValueError("Insufficient data for scaled uint32 parsing")
        raw_value = DataParser.parse_int32(data, offset, signed=False)
        return raw_value * self.scale_factor

    def encode_value(self, value: float) -> bytearray:
        """Encode scaled value to bytes."""
        raw_value = int(value / self.scale_factor)
        if not 0 <= raw_value <= UINT32_MAX:
            raise ValueError(f"Scaled value {raw_value} out of range for uint32")
        return DataParser.encode_int32(raw_value, signed=False)


class ScaledUint24Template(CodingTemplate):
    """Template for scaled 24-bit unsigned integer with configurable resolution.

    Used for values encoded in 3 bytes as unsigned integers.
    Example: Illuminance 1000 lux stored as bytes with scale_factor=1.0
    """

    def __init__(self, scale_factor: float = 1.0) -> None:
        """Initialize with scale factor.

        Args:
            scale_factor: Factor to multiply raw value by

        """
        self.scale_factor = scale_factor

    @property
    def data_size(self) -> int:
        """Size: 3 bytes."""
        return 3

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> float:
        """Parse scaled 24-bit unsigned integer."""
        if len(data) < offset + 3:
            raise ValueError("Insufficient data for scaled uint24 parsing")
        raw_value = int.from_bytes(data[offset : offset + 3], byteorder="little", signed=False)
        return raw_value * self.scale_factor

    def encode_value(self, value: float) -> bytearray:
        """Encode scaled value to 3 bytes."""
        raw_value = int(value / self.scale_factor)
        if not 0 <= raw_value <= UINT24_MAX:
            raise ValueError(f"Scaled value {raw_value} out of range for uint24")
        return bytearray(raw_value.to_bytes(3, byteorder="little", signed=False))


class ScaledSint24Template(CodingTemplate):
    """Template for scaled 24-bit signed integer with configurable resolution.

    Used for signed values encoded in 3 bytes.
    Example: Elevation 500.00m stored as bytes with scale_factor=0.01
    """

    def __init__(self, scale_factor: float = 0.01) -> None:
        """Initialize with scale factor.

        Args:
            scale_factor: Factor to multiply raw value by

        """
        self.scale_factor = scale_factor

    @property
    def data_size(self) -> int:
        """Size: 3 bytes."""
        return 3

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> float:
        """Parse scaled 24-bit signed integer."""
        if len(data) < offset + 3:
            raise ValueError("Insufficient data for scaled sint24 parsing")
        # Parse as unsigned first
        raw_unsigned = int.from_bytes(data[offset : offset + 3], byteorder="little", signed=False)
        # Convert to signed using two's complement
        if raw_unsigned >= 0x800000:  # Sign bit set (2^23)
            raw_value = raw_unsigned - 0x1000000  # 2^24
        else:
            raw_value = raw_unsigned
        return raw_value * self.scale_factor

    def encode_value(self, value: float) -> bytearray:
        """Encode scaled value to 3 bytes."""
        raw_value = int(value / self.scale_factor)
        if not SINT24_MIN <= raw_value <= SINT24_MAX:
            raise ValueError(f"Scaled value {raw_value} out of range for sint24")
        # Convert to unsigned representation if negative
        if raw_value < 0:
            raw_unsigned = raw_value + 0x1000000  # 2^24
        else:
            raw_unsigned = raw_value
        return bytearray(raw_unsigned.to_bytes(3, byteorder="little", signed=False))


# =============================================================================
# DOMAIN-SPECIFIC TEMPLATES
# =============================================================================


class PercentageTemplate(CodingTemplate):
    """Template for percentage values (0-100%) using uint8."""

    @property
    def data_size(self) -> int:
        """Size: 1 byte."""
        return 1

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> int:
        """Parse percentage value."""
        if len(data) < offset + 1:
            raise ValueError("Insufficient data for percentage parsing")
        value = DataParser.parse_int8(data, offset, signed=False)
        if not 0 <= value <= PERCENTAGE_MAX:
            raise ValueError(f"Percentage value {value} out of range (0-{PERCENTAGE_MAX})")
        return value

    def encode_value(self, value: int) -> bytearray:
        """Encode percentage value to bytes."""
        if not 0 <= value <= PERCENTAGE_MAX:
            raise ValueError(f"Percentage value {value} out of range (0-{PERCENTAGE_MAX})")
        return DataParser.encode_int8(value, signed=False)


class TemperatureTemplate(CodingTemplate):
    """Template for standard Bluetooth SIG temperature format (sint16, 0.01°C resolution)."""

    def __init__(self) -> None:
        """Initialize with standard temperature resolution."""
        self._scaled_template = ScaledSint16Template(scale_factor=TEMPERATURE_RESOLUTION)

    @property
    def data_size(self) -> int:
        """Size: 2 bytes."""
        return 2

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> float:
        """Parse temperature in 0.01°C resolution."""
        return self._scaled_template.decode_value(data, offset)

    def encode_value(self, value: float) -> bytearray:
        """Encode temperature to bytes."""
        return self._scaled_template.encode_value(value)


class ConcentrationTemplate(CodingTemplate):
    """Template for concentration measurements with configurable resolution.

    Used for environmental sensors like CO2, VOC, particulate matter, etc.
    """

    def __init__(self, resolution: float = 1.0) -> None:
        """Initialize with resolution.

        Args:
            resolution: Measurement resolution (e.g., 1.0 for integer ppm, 0.1 for 0.1 ppm)

        """
        self._scaled_template = ScaledUint16Template(scale_factor=resolution)

    @property
    def data_size(self) -> int:
        """Size: 2 bytes."""
        return 2

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> float:
        """Parse concentration with resolution."""
        return self._scaled_template.decode_value(data, offset)

    def encode_value(self, value: float) -> bytearray:
        """Encode concentration value to bytes."""
        return self._scaled_template.encode_value(value)


class PressureTemplate(CodingTemplate):
    """Template for pressure measurements (uint32, 0.1 Pa resolution)."""

    def __init__(self) -> None:
        """Initialize with standard pressure resolution (0.1 Pa)."""
        self._scaled_template = ScaledUint32Template(scale_factor=0.1)

    @property
    def data_size(self) -> int:
        """Size: 4 bytes."""
        return 4

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> float:
        """Parse pressure in 0.1 Pa resolution (returns Pa)."""
        return self._scaled_template.decode_value(data, offset)

    def encode_value(self, value: float) -> bytearray:
        """Encode pressure to bytes."""
        return self._scaled_template.encode_value(value)


class IEEE11073FloatTemplate(CodingTemplate):
    """Template for IEEE 11073 SFLOAT format (16-bit medical device float)."""

    @property
    def data_size(self) -> int:
        """Size: 2 bytes."""
        return 2

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> float:
        """Parse IEEE 11073 SFLOAT format."""
        if len(data) < offset + 2:
            raise ValueError("Insufficient data for IEEE11073 SFLOAT parsing")
        return IEEE11073Parser.parse_sfloat(data, offset)

    def encode_value(self, value: float) -> bytearray:
        """Encode value to IEEE 11073 SFLOAT format."""
        return IEEE11073Parser.encode_sfloat(value)


class Float32Template(CodingTemplate):
    """Template for IEEE-754 32-bit float parsing."""

    @property
    def data_size(self) -> int:
        """Size: 4 bytes."""
        return 4

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> float:
        """Parse IEEE-754 32-bit float."""
        if len(data) < offset + 4:
            raise ValueError("Insufficient data for float32 parsing")
        return DataParser.parse_float32(data, offset)

    def encode_value(self, value: float) -> bytearray:
        """Encode float32 value to bytes."""
        return DataParser.encode_float32(float(value))


# =============================================================================
# STRING TEMPLATES
# =============================================================================


class Utf8StringTemplate(CodingTemplate):
    """Template for UTF-8 string parsing with variable length."""

    def __init__(self, max_length: int = 256) -> None:
        """Initialize with maximum string length.

        Args:
            max_length: Maximum string length in bytes

        """
        self.max_length = max_length

    @property
    def data_size(self) -> int:
        """Size: Variable (0 to max_length)."""
        return self.max_length

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> str:
        """Parse UTF-8 string from remaining data."""
        if offset >= len(data):
            return ""

        # Take remaining data from offset
        string_data = data[offset:]

        # Remove null terminator if present
        if b"\x00" in string_data:
            null_index = string_data.index(b"\x00")
            string_data = string_data[:null_index]

        try:
            return string_data.decode("utf-8")
        except UnicodeDecodeError as e:
            raise ValueError(f"Invalid UTF-8 string data: {e}") from e

    def encode_value(self, value: str) -> bytearray:
        """Encode string to UTF-8 bytes."""
        encoded = value.encode("utf-8")
        if len(encoded) > self.max_length:
            raise ValueError(f"String too long: {len(encoded)} > {self.max_length}")
        return bytearray(encoded)


# =============================================================================
# VECTOR TEMPLATES
# =============================================================================


class VectorTemplate(CodingTemplate):
    """Template for 3D vector measurements (x, y, z float32 components)."""

    @property
    def data_size(self) -> int:
        """Size: 12 bytes (3 x float32)."""
        return 12

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> VectorData:
        """Parse 3D vector data."""
        if len(data) < offset + 12:
            raise ValueError("Insufficient data for 3D vector parsing (need 12 bytes)")

        x_axis = DataParser.parse_float32(data, offset)
        y_axis = DataParser.parse_float32(data, offset + 4)
        z_axis = DataParser.parse_float32(data, offset + 8)

        return VectorData(x_axis=x_axis, y_axis=y_axis, z_axis=z_axis)

    def encode_value(self, value: VectorData) -> bytearray:
        """Encode 3D vector data to bytes."""
        result = bytearray()
        result.extend(DataParser.encode_float32(value.x_axis))
        result.extend(DataParser.encode_float32(value.y_axis))
        result.extend(DataParser.encode_float32(value.z_axis))
        return result


class Vector2DTemplate(CodingTemplate):
    """Template for 2D vector measurements (x, y float32 components)."""

    @property
    def data_size(self) -> int:
        """Size: 8 bytes (2 x float32)."""
        return 8

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> Vector2DData:
        """Parse 2D vector data."""
        if len(data) < offset + 8:
            raise ValueError("Insufficient data for 2D vector parsing (need 8 bytes)")

        x_axis = DataParser.parse_float32(data, offset)
        y_axis = DataParser.parse_float32(data, offset + 4)

        return Vector2DData(x_axis=x_axis, y_axis=y_axis)

    def encode_value(self, value: Vector2DData) -> bytearray:
        """Encode 2D vector data to bytes."""
        result = bytearray()
        result.extend(DataParser.encode_float32(value.x_axis))
        result.extend(DataParser.encode_float32(value.y_axis))
        return result


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Protocol
    "CodingTemplate",
    # Data structures
    "VectorData",
    "Vector2DData",
    # Basic integer templates
    "Uint8Template",
    "Sint8Template",
    "Uint16Template",
    "Sint16Template",
    "Uint32Template",
    # Scaled templates
    "ScaledUint16Template",
    "ScaledSint16Template",
    "ScaledUint32Template",
    "ScaledUint24Template",
    "ScaledSint24Template",
    # Domain-specific templates
    "PercentageTemplate",
    "TemperatureTemplate",
    "ConcentrationTemplate",
    "PressureTemplate",
    "IEEE11073FloatTemplate",
    "Float32Template",
    # String templates
    "Utf8StringTemplate",
    # Vector templates
    "VectorTemplate",
    "Vector2DTemplate",
]
