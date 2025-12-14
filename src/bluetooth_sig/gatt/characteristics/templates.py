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
from datetime import datetime
from typing import Any

import msgspec

from ...types.gatt_enums import AdjustReason, DayOfWeek
from ..constants import (
    PERCENTAGE_MAX,
    SINT8_MAX,
    SINT8_MIN,
    SINT16_MAX,
    SINT16_MIN,
    SINT24_MAX,
    SINT24_MIN,
    UINT8_MAX,
    UINT16_MAX,
    UINT24_MAX,
    UINT32_MAX,
)
from ..context import CharacteristicContext
from ..exceptions import InsufficientDataError, ValueRangeError
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


class TimeData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Time characteristic data structure."""

    date_time: datetime | None
    day_of_week: DayOfWeek
    fractions256: int
    adjust_reason: AdjustReason


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


class ScaledTemplate(CodingTemplate):
    """Base class for scaled integer templates.

    Handles common scaling logic: value = (raw + offset) * scale_factor
    Subclasses implement raw parsing/encoding and range checking.
    """

    def __init__(self, scale_factor: float, offset: int) -> None:
        """Initialize with scale factor and offset.

        Args:
            scale_factor: Factor to multiply raw value by
            offset: Offset to add to raw value before scaling

        """
        self.scale_factor = scale_factor
        self.offset = offset

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> float:
        """Parse scaled integer value."""
        raw_value = self._parse_raw(data, offset)
        return (raw_value + self.offset) * self.scale_factor

    def encode_value(self, value: float) -> bytearray:
        """Encode scaled value to bytes."""
        raw_value = int((value / self.scale_factor) - self.offset)
        self._check_range(raw_value)
        return self._encode_raw(raw_value)

    @abstractmethod
    def _parse_raw(self, data: bytearray, offset: int) -> int:
        """Parse raw integer value from data."""

    @abstractmethod
    def _encode_raw(self, raw: int) -> bytearray:
        """Encode raw integer to bytes."""

    @abstractmethod
    def _check_range(self, raw: int) -> None:
        """Check if raw value is in valid range."""

    @classmethod
    def from_scale_offset(cls, scale_factor: float, offset: int) -> ScaledTemplate:
        """Create instance using scale factor and offset.

        Args:
            scale_factor: Factor to multiply raw value by
            offset: Offset to add to raw value before scaling

        Returns:
            ScaledSint8Template instance

        """
        return cls(scale_factor=scale_factor, offset=offset)

    @classmethod
    def from_letter_method(cls, M: int, d: int, b: int) -> ScaledTemplate:
        """Create instance using Bluetooth SIG M, d, b parameters.

        Args:
            M: Multiplier factor
            d: Decimal exponent (10^d)
            b: Offset to add to raw value before scaling

        Returns:
            ScaledUint16Template instance

        """
        scale_factor = M * (10**d)
        return cls(scale_factor=scale_factor, offset=b)


class ScaledUint16Template(ScaledTemplate):
    """Template for scaled 16-bit unsigned integer.

    Used for values that need decimal precision encoded as integers.
    Can be initialized with scale_factor/offset or Bluetooth SIG M, d, b parameters.
    Formula: value = scale_factor * (raw + offset) or value = M * 10^d * (raw + b)
    Example: Temperature 25.5°C stored as 2550 with scale_factor=0.01, offset=0 or M=1, d=-2, b=0
    """

    def __init__(self, scale_factor: float = 1.0, offset: int = 0) -> None:
        """Initialize with scale factor and offset.

        Args:
            scale_factor: Factor to multiply raw value by
            offset: Offset to add to raw value before scaling

        """
        super().__init__(scale_factor, offset)

    @property
    def data_size(self) -> int:
        """Size: 2 bytes."""
        return 2

    def _parse_raw(self, data: bytearray, offset: int) -> int:
        """Parse raw 16-bit unsigned integer."""
        if len(data) < offset + 2:
            raise ValueError("Insufficient data for scaled uint16 parsing")
        return DataParser.parse_int16(data, offset, signed=False)

    def _encode_raw(self, raw: int) -> bytearray:
        """Encode raw 16-bit unsigned integer."""
        return DataParser.encode_int16(raw, signed=False)

    def _check_range(self, raw: int) -> None:
        """Check range for uint16."""
        if not 0 <= raw <= UINT16_MAX:
            raise ValueError(f"Scaled value {raw} out of range for uint16")


class ScaledSint16Template(ScaledTemplate):
    """Template for scaled 16-bit signed integer.

    Used for signed values that need decimal precision encoded as integers.
    Can be initialized with scale_factor/offset or Bluetooth SIG M, d, b parameters.
    Formula: value = scale_factor * (raw + offset) or value = M * 10^d * (raw + b)
    Example: Temperature -10.5°C stored as -1050 with scale_factor=0.01, offset=0 or M=1, d=-2, b=0
    """

    def __init__(self, scale_factor: float = 0.01, offset: int = 0) -> None:
        """Initialize with scale factor and offset.

        Args:
            scale_factor: Factor to multiply raw value by
            offset: Offset to add to raw value before scaling

        """
        super().__init__(scale_factor, offset)

    @property
    def data_size(self) -> int:
        """Size: 2 bytes."""
        return 2

    def _parse_raw(self, data: bytearray, offset: int) -> int:
        """Parse raw 16-bit signed integer."""
        if len(data) < offset + 2:
            raise ValueError("Insufficient data for scaled sint16 parsing")
        return DataParser.parse_int16(data, offset, signed=True)

    def _encode_raw(self, raw: int) -> bytearray:
        """Encode raw 16-bit signed integer."""
        return DataParser.encode_int16(raw, signed=True)

    def _check_range(self, raw: int) -> None:
        """Check range for sint16."""
        if not SINT16_MIN <= raw <= SINT16_MAX:
            raise ValueError(f"Scaled value {raw} out of range for sint16")


class ScaledSint8Template(ScaledTemplate):
    """Template for scaled 8-bit signed integer.

    Used for signed values that need decimal precision encoded as integers.
    Can be initialized with scale_factor/offset or Bluetooth SIG M, d, b parameters.
    Formula: value = scale_factor * (raw + offset) or value = M * 10^d * (raw + b)
    Example: Temperature with scale_factor=0.01, offset=0 or M=1, d=-2, b=0
    """

    def __init__(self, scale_factor: float = 1.0, offset: int = 0) -> None:
        """Initialize with scale factor and offset.

        Args:
            scale_factor: Factor to multiply raw value by
            offset: Offset to add to raw value before scaling

        """
        super().__init__(scale_factor, offset)

    @property
    def data_size(self) -> int:
        """Size: 1 byte."""
        return 1

    def _parse_raw(self, data: bytearray, offset: int) -> int:
        """Parse raw 8-bit signed integer."""
        if len(data) < offset + 1:
            raise ValueError("Insufficient data for scaled sint8 parsing")
        return DataParser.parse_int8(data, offset, signed=True)

    def _encode_raw(self, raw: int) -> bytearray:
        """Encode raw 8-bit signed integer."""
        return DataParser.encode_int8(raw, signed=True)

    def _check_range(self, raw: int) -> None:
        """Check range for sint8."""
        if not SINT8_MIN <= raw <= SINT8_MAX:
            raise ValueError(f"Scaled value {raw} out of range for sint8")


class ScaledUint8Template(ScaledTemplate):
    """Template for scaled 8-bit unsigned integer.

    Used for unsigned values that need decimal precision encoded as integers.
    Can be initialized with scale_factor/offset or Bluetooth SIG M, d, b parameters.
    Formula: value = scale_factor * (raw + offset) or value = M * 10^d * (raw + b)
    Example: Uncertainty with scale_factor=0.1, offset=0 or M=1, d=-1, b=0
    """

    def __init__(self, scale_factor: float = 1.0, offset: int = 0) -> None:
        """Initialize with scale factor and offset.

        Args:
            scale_factor: Factor to multiply raw value by
            offset: Offset to add to raw value before scaling

        """
        super().__init__(scale_factor, offset)

    @property
    def data_size(self) -> int:
        """Size: 1 byte."""
        return 1

    def _parse_raw(self, data: bytearray, offset: int) -> int:
        """Parse raw 8-bit unsigned integer."""
        if len(data) < offset + 1:
            raise ValueError("Insufficient data for scaled uint8 parsing")
        return DataParser.parse_int8(data, offset, signed=False)

    def _encode_raw(self, raw: int) -> bytearray:
        """Encode raw 8-bit unsigned integer."""
        return DataParser.encode_int8(raw, signed=False)

    def _check_range(self, raw: int) -> None:
        """Check range for uint8."""
        if not 0 <= raw <= UINT8_MAX:
            raise ValueError(f"Scaled value {raw} out of range for uint8")


class ScaledUint32Template(ScaledTemplate):
    """Template for scaled 32-bit unsigned integer with configurable resolution and offset."""

    def __init__(self, scale_factor: float = 0.1, offset: int = 0) -> None:
        """Initialize with scale factor and offset.

        Args:
            scale_factor: Factor to multiply raw value by (e.g., 0.1 for 1 decimal place)
            offset: Offset to add to raw value before scaling

        """
        super().__init__(scale_factor, offset)

    @property
    def data_size(self) -> int:
        """Size: 4 bytes."""
        return 4

    def _parse_raw(self, data: bytearray, offset: int) -> int:
        """Parse raw 32-bit unsigned integer."""
        if len(data) < offset + 4:
            raise ValueError("Insufficient data for scaled uint32 parsing")
        return DataParser.parse_int32(data, offset, signed=False)

    def _encode_raw(self, raw: int) -> bytearray:
        """Encode raw 32-bit unsigned integer."""
        return DataParser.encode_int32(raw, signed=False)

    def _check_range(self, raw: int) -> None:
        """Check range for uint32."""
        if not 0 <= raw <= UINT32_MAX:
            raise ValueError(f"Scaled value {raw} out of range for uint32")


class ScaledUint24Template(ScaledTemplate):
    """Template for scaled 24-bit unsigned integer with configurable resolution and offset.

    Used for values encoded in 3 bytes as unsigned integers.
    Example: Illuminance 1000 lux stored as bytes with scale_factor=1.0, offset=0
    """

    def __init__(self, scale_factor: float = 1.0, offset: int = 0) -> None:
        """Initialize with scale factor and offset.

        Args:
            scale_factor: Factor to multiply raw value by
            offset: Offset to add to raw value before scaling

        """
        super().__init__(scale_factor, offset)

    @property
    def data_size(self) -> int:
        """Size: 3 bytes."""
        return 3

    def _parse_raw(self, data: bytearray, offset: int) -> int:
        """Parse raw 24-bit unsigned integer."""
        if len(data) < offset + 3:
            raise ValueError("Insufficient data for scaled uint24 parsing")
        return int.from_bytes(data[offset : offset + 3], byteorder="little", signed=False)

    def _encode_raw(self, raw: int) -> bytearray:
        """Encode raw 24-bit unsigned integer."""
        return bytearray(raw.to_bytes(3, byteorder="little", signed=False))

    def _check_range(self, raw: int) -> None:
        """Check range for uint24."""
        if not 0 <= raw <= UINT24_MAX:
            raise ValueError(f"Scaled value {raw} out of range for uint24")


class ScaledSint24Template(ScaledTemplate):
    """Template for scaled 24-bit signed integer with configurable resolution and offset.

    Used for signed values encoded in 3 bytes.
    Example: Elevation 500.00m stored as bytes with scale_factor=0.01, offset=0
    """

    def __init__(self, scale_factor: float = 0.01, offset: int = 0) -> None:
        """Initialize with scale factor and offset.

        Args:
            scale_factor: Factor to multiply raw value by
            offset: Offset to add to raw value before scaling

        """
        super().__init__(scale_factor, offset)

    @property
    def data_size(self) -> int:
        """Size: 3 bytes."""
        return 3

    def _parse_raw(self, data: bytearray, offset: int) -> int:
        """Parse raw 24-bit signed integer."""
        if len(data) < offset + 3:
            raise ValueError("Insufficient data for scaled sint24 parsing")
        # Parse as unsigned first
        raw_unsigned = int.from_bytes(data[offset : offset + 3], byteorder="little", signed=False)
        # Convert to signed using two's complement
        if raw_unsigned >= 0x800000:  # Sign bit set (2^23)
            raw_value = raw_unsigned - 0x1000000  # 2^24
        else:
            raw_value = raw_unsigned
        return raw_value

    def _encode_raw(self, raw: int) -> bytearray:
        """Encode raw 24-bit signed integer."""
        # Convert to unsigned representation if negative
        if raw < 0:
            raw_unsigned = raw + 0x1000000  # 2^24
        else:
            raw_unsigned = raw
        return bytearray(raw_unsigned.to_bytes(3, byteorder="little", signed=False))

    def _check_range(self, raw: int) -> None:
        """Check range for sint24."""
        if not SINT24_MIN <= raw <= SINT24_MAX:
            raise ValueError(f"Scaled value {raw} out of range for sint24")


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
        self._scaled_template = ScaledSint16Template.from_letter_method(1, -2, 0)

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
        # Convert resolution to M, d, b parameters when it fits the pattern
        # resolution = M * 10^d, so we find M and d such that M * 10^d = resolution
        if resolution == 1.0:
            # resolution = 1 * 10^0
            self._scaled_template = ScaledUint16Template.from_letter_method(M=1, d=0, b=0)
        elif resolution == 0.1:
            # resolution = 1 * 10^-1
            self._scaled_template = ScaledUint16Template.from_letter_method(M=1, d=-1, b=0)
        elif resolution == 0.01:
            # resolution = 1 * 10^-2
            self._scaled_template = ScaledUint16Template.from_letter_method(M=1, d=-2, b=0)
        else:
            # Fallback to scale_factor for resolutions that don't fit M * 10^d pattern
            self._scaled_template = ScaledUint16Template(scale_factor=resolution)

    @classmethod
    def from_letter_method(cls, M: int, d: int, b: int = 0) -> ConcentrationTemplate:
        """Create instance using Bluetooth SIG M, d, b parameters.

        Args:
            M: Multiplier factor
            d: Decimal exponent (10^d)
            b: Offset to add to raw value before scaling

        Returns:
            ConcentrationTemplate instance

        """
        instance = cls.__new__(cls)
        instance._scaled_template = ScaledUint16Template.from_letter_method(M=M, d=d, b=b)
        return instance

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


class TimeDataTemplate(CodingTemplate):
    """Template for Bluetooth SIG time data parsing (10 bytes).

    Used for Current Time and Time with DST characteristics.
    Structure: Date Time (7 bytes) + Day of Week (1) + Fractions256 (1) + Adjust Reason (1)
    """

    LENGTH = 10
    DAY_OF_WEEK_MAX = 7
    FRACTIONS256_MAX = 255
    ADJUST_REASON_MAX = 255

    @property
    def data_size(self) -> int:
        """Size: 10 bytes."""
        return self.LENGTH

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> TimeData:
        """Parse time data from bytes."""
        if len(data) < offset + self.LENGTH:
            raise InsufficientDataError("time data", data[offset:], self.LENGTH)

        # Parse Date Time (7 bytes)
        year = DataParser.parse_int16(data, offset, signed=False)
        month = data[offset + 2]
        day = data[offset + 3]

        if year == 0 or month == 0 or day == 0:
            date_time = None
        else:
            date_time = IEEE11073Parser.parse_timestamp(data, offset)

        # Parse Day of Week (1 byte)
        day_of_week_raw = data[offset + 7]
        if day_of_week_raw > self.DAY_OF_WEEK_MAX:
            raise ValueRangeError("day_of_week", day_of_week_raw, 0, self.DAY_OF_WEEK_MAX)
        day_of_week = DayOfWeek(day_of_week_raw)

        # Parse Fractions256 (1 byte)
        fractions256 = data[offset + 8]

        # Parse Adjust Reason (1 byte)
        adjust_reason = AdjustReason.from_raw(data[offset + 9])

        return TimeData(
            date_time=date_time, day_of_week=day_of_week, fractions256=fractions256, adjust_reason=adjust_reason
        )

    def encode_value(self, value: TimeData) -> bytearray:
        """Encode time data to bytes."""
        result = bytearray()

        # Encode Date Time (7 bytes)
        if value.date_time is None:
            result.extend(bytearray(IEEE11073Parser.TIMESTAMP_LENGTH))
        else:
            result.extend(IEEE11073Parser.encode_timestamp(value.date_time))

        # Encode Day of Week (1 byte)
        day_of_week_value = int(value.day_of_week)
        if day_of_week_value > self.DAY_OF_WEEK_MAX:
            raise ValueRangeError("day_of_week", day_of_week_value, 0, self.DAY_OF_WEEK_MAX)
        result.append(day_of_week_value)

        # Encode Fractions256 (1 byte)
        if value.fractions256 > self.FRACTIONS256_MAX:
            raise ValueRangeError("fractions256", value.fractions256, 0, self.FRACTIONS256_MAX)
        result.append(value.fractions256)

        # Encode Adjust Reason (1 byte)
        if int(value.adjust_reason) > self.ADJUST_REASON_MAX:
            raise ValueRangeError("adjust_reason", int(value.adjust_reason), 0, self.ADJUST_REASON_MAX)
        result.append(int(value.adjust_reason))

        return result


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


class Utf16StringTemplate(CodingTemplate):
    """Template for UTF-16LE string parsing with variable length."""

    # Unicode constants for UTF-16 validation
    UNICODE_SURROGATE_START = 0xD800
    UNICODE_SURROGATE_END = 0xDFFF
    UNICODE_BOM = "\ufeff"

    def __init__(self, max_length: int = 256) -> None:
        """Initialize with maximum string length.

        Args:
            max_length: Maximum string length in bytes (must be even)

        """
        if max_length % 2 != 0:
            raise ValueError("max_length must be even for UTF-16 strings")
        self.max_length = max_length

    @property
    def data_size(self) -> int:
        """Size: Variable (0 to max_length, even bytes only)."""
        return self.max_length

    def decode_value(self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None) -> str:
        """Parse UTF-16LE string from remaining data."""
        if offset >= len(data):
            return ""

        # Take remaining data from offset
        string_data = data[offset:]

        # Find null terminator at even positions (UTF-16 alignment)
        null_index = len(string_data)
        for i in range(0, len(string_data) - 1, 2):
            if string_data[i : i + 2] == bytearray(b"\x00\x00"):
                null_index = i
                break
        string_data = string_data[:null_index]

        # UTF-16 requires even number of bytes
        if len(string_data) % 2 != 0:
            raise ValueError(f"UTF-16 data must have even byte count, got {len(string_data)}")

        try:
            decoded = string_data.decode("utf-16-le")
            # Strip BOM if present (robustness)
            if decoded.startswith(self.UNICODE_BOM):
                decoded = decoded[1:]
            # Check for invalid surrogate pairs
            if any(self.UNICODE_SURROGATE_START <= ord(c) <= self.UNICODE_SURROGATE_END for c in decoded):
                raise ValueError("Invalid UTF-16LE string data: contains unpaired surrogates")
            return decoded
        except UnicodeDecodeError as e:
            raise ValueError(f"Invalid UTF-16LE string data: {e}") from e

    def encode_value(self, value: str) -> bytearray:
        """Encode string to UTF-16LE bytes."""
        encoded = value.encode("utf-16-le")
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
    "TimeData",
    # Basic integer templates
    "Uint8Template",
    "Sint8Template",
    "Uint16Template",
    "Sint16Template",
    "Uint32Template",
    # Scaled templates
    "ScaledUint16Template",
    "ScaledSint16Template",
    "ScaledSint8Template",
    "ScaledUint8Template",
    "ScaledUint32Template",
    "ScaledUint24Template",
    "ScaledSint24Template",
    # Domain-specific templates
    "PercentageTemplate",
    "TemperatureTemplate",
    "ConcentrationTemplate",
    "PressureTemplate",
    "TimeDataTemplate",
    "IEEE11073FloatTemplate",
    "Float32Template",
    # String templates
    "Utf8StringTemplate",
    "Utf16StringTemplate",
    # Vector templates
    "VectorTemplate",
    "Vector2DTemplate",
]
