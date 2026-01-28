"""Value translators for the BLE encoding/decoding pipeline.

This module provides the translation layer that converts raw integers to domain
values (and back). Translators have a single responsibility: value interpretation
and scaling.

The translation layer is the second stage of the decode pipeline:
    bytes → [Extractor] → raw_int → [Translator] → typed_value

Translators do NOT handle:
- Byte extraction (that's the extractor's job)
- Special value detection (that's a pipeline interception point)
- Validation (that's a separate validation layer)
"""

from __future__ import annotations

import struct
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from .ieee11073_parser import IEEE11073Parser

T = TypeVar("T")


class ValueTranslator(ABC, Generic[T]):
    """Protocol for raw-to-value translation.

    Translators convert raw integer values to typed domain values and back.
    They handle scaling, offset, and type conversion but NOT:
    - Byte extraction (use RawExtractor)
    - Special value handling (pipeline intercepts before translation)
    - Validation (separate validation layer)

    Type parameter T is the output type (int, float, etc.).
    """

    __slots__ = ()

    @abstractmethod
    def translate(self, raw: int) -> T:
        """Convert raw integer to domain value.

        Args:
            raw: Raw integer from extractor.

        Returns:
            Typed domain value.
        """

    @abstractmethod
    def untranslate(self, value: T) -> int:
        """Convert domain value back to raw integer.

        Args:
            value: Typed domain value.

        Returns:
            Raw integer for encoder.

        Raises:
            ValueError: If value cannot be converted to raw integer.
        """


class IdentityTranslator(ValueTranslator[int]):
    """Pass-through translator for values needing no conversion.

    Used for simple integer types where raw == domain value.
    """

    __slots__ = ()

    def translate(self, raw: int) -> int:
        """Return raw value unchanged."""
        return raw

    def untranslate(self, value: int) -> int:
        """Return value unchanged."""
        return value


class LinearTranslator(ValueTranslator[float]):
    """Linear scaling translator: value = (raw + offset) * scale_factor.

    This implements the Bluetooth SIG M, d, b formula:
        actual_value = M * 10^d * (raw + b)

    Where:
        scale_factor = M * 10^d
        offset = b

    Examples:
        Temperature 0.01°C resolution: LinearTranslator(scale_factor=0.01, offset=0)
        Humidity 0.01% resolution: LinearTranslator(scale_factor=0.01, offset=0)
    """

    __slots__ = ("_offset", "_scale_factor")

    def __init__(self, scale_factor: float = 1.0, offset: int = 0) -> None:
        """Initialize with scaling parameters.

        Args:
            scale_factor: Multiplier applied after offset (M * 10^d).
            offset: Value added to raw before scaling (b).
        """
        self._scale_factor = scale_factor
        self._offset = offset

    @classmethod
    def from_mdb(cls, m: int, d: int, b: int) -> LinearTranslator:
        """Create from Bluetooth SIG M, d, b parameters.

        Args:
            m: Multiplier factor.
            d: Decimal exponent (10^d).
            b: Offset added to raw value.

        Returns:
            Configured LinearTranslator instance.

        Examples:
            Temperature 0.01°C: from_mdb(1, -2, 0)
            Percentage 0.5%: from_mdb(5, -1, 0)
        """
        scale_factor = m * (10**d)
        return cls(scale_factor=scale_factor, offset=b)

    @property
    def scale_factor(self) -> float:
        """Get the scale factor (M * 10^d)."""
        return self._scale_factor

    @property
    def offset(self) -> int:
        """Return the offset value (b parameter)."""
        return self._offset

    def translate(self, raw: int) -> float:
        """Apply linear scaling: (raw + offset) * scale_factor."""
        return (raw + self._offset) * self._scale_factor

    def untranslate(self, value: float) -> int:
        """Reverse linear scaling: (value / scale_factor) - offset."""
        return int((value / self._scale_factor) - self._offset)


class PercentageTranslator(ValueTranslator[int]):
    """Translator for percentage values (0-100).

    Simple pass-through since percentage is typically stored as uint8 0-100.
    Provides semantic clarity in the pipeline.
    """

    __slots__ = ()

    def translate(self, raw: int) -> int:
        """Return percentage value."""
        return raw

    def untranslate(self, value: int) -> int:
        """Return percentage as raw."""
        return value


class SfloatTranslator(ValueTranslator[float]):
    """Translator for IEEE 11073 16-bit SFLOAT format.

    SFLOAT is used by many Bluetooth Health profiles (blood pressure,
    glucose, weight scale, etc.). It provides a compact representation
    with ~3 significant digits.

    Special value handling:
    - 0x07FF: NaN
    - 0x0800: NRes (Not at this resolution)
    - 0x07FE: +INFINITY
    - 0x0802: -INFINITY
    """

    __slots__ = ()

    NAN = 0x07FF
    NRES = 0x0800
    POSITIVE_INFINITY = 0x07FE
    NEGATIVE_INFINITY = 0x0802

    def translate(self, raw: int) -> float:
        """Convert raw SFLOAT bits to float value.

        Args:
            raw: Raw 16-bit integer from extractor.

        Returns:
            Decoded float value, or NaN/Inf for special values.
        """
        raw_bytes = raw.to_bytes(2, byteorder="little", signed=False)
        return IEEE11073Parser.parse_sfloat(raw_bytes, offset=0)

    def untranslate(self, value: float) -> int:
        """Encode float to SFLOAT raw bits.

        Args:
            value: Float value to encode.

        Returns:
            Raw 16-bit integer for extractor.
        """
        encoded = IEEE11073Parser.encode_sfloat(value)
        return int.from_bytes(encoded, byteorder="little", signed=False)


class Float32IEEETranslator(ValueTranslator[float]):
    """Translator for IEEE 11073 32-bit FLOAT format (medfloat32).

    Used by medical device profiles for higher precision measurements.
    """

    __slots__ = ()

    # Per IEEE 11073-20601 and Bluetooth GSS special values (exponent=0)
    NAN = 0x007FFFFF  # Mantissa 0x7FFFFF
    NRES = 0x00800000  # Mantissa 0x800000
    RFU = 0x00800001  # Mantissa 0x800001 (Reserved for Future Use)
    POSITIVE_INFINITY = 0x007FFFFE  # Mantissa 0x7FFFFE
    NEGATIVE_INFINITY = 0x00800002  # Mantissa 0x800002

    def translate(self, raw: int) -> float:
        """Convert raw FLOAT32 bits to float value."""
        raw_bytes = raw.to_bytes(4, byteorder="little", signed=False)
        return IEEE11073Parser.parse_float32(raw_bytes, offset=0)

    def untranslate(self, value: float) -> int:
        """Encode float to FLOAT32 raw bits."""
        encoded = IEEE11073Parser.encode_float32(value)
        return int.from_bytes(encoded, byteorder="little", signed=False)


class Float32IEEE754Translator(ValueTranslator[float]):
    """Translator for standard IEEE-754 32-bit float (not IEEE 11073).

    For characteristics using standard single-precision floats rather
    than the medical device FLOAT32 format.
    """

    __slots__ = ()

    def translate(self, raw: int) -> float:
        """Convert raw bits to IEEE-754 float."""
        raw_bytes = raw.to_bytes(4, byteorder="little", signed=False)
        return float(struct.unpack("<f", raw_bytes)[0])

    def untranslate(self, value: float) -> int:
        """Encode IEEE-754 float to raw bits."""
        raw_bytes = struct.pack("<f", value)
        return int.from_bytes(raw_bytes, byteorder="little", signed=False)


# Singleton instances for stateless translators
IDENTITY = IdentityTranslator()
PERCENTAGE = PercentageTranslator()
SFLOAT = SfloatTranslator()
FLOAT32_IEEE11073 = Float32IEEETranslator()
FLOAT32_IEEE754 = Float32IEEE754Translator()


def create_linear_translator(
    scale_factor: float | None = None,
    offset: int = 0,
    m: int | None = None,
    d: int | None = None,
    b: int | None = None,
) -> LinearTranslator:
    """Factory for creating LinearTranslator instances.

    Can be configured either with scale_factor/offset or M/d/b parameters.

    Args:
        scale_factor: Direct scale factor (takes precedence over M/d).
        offset: Direct offset (takes precedence over b).
        m: Bluetooth SIG multiplier.
        d: Bluetooth SIG decimal exponent.
        b: Bluetooth SIG offset.

    Returns:
        Configured LinearTranslator.

    Examples:
        >>> temp_translator = create_linear_translator(scale_factor=0.01)
        >>> temp_translator = create_linear_translator(m=1, d=-2, b=0)
    """
    if scale_factor is not None:
        return LinearTranslator(scale_factor=scale_factor, offset=offset)

    if m is not None and d is not None:
        return LinearTranslator.from_mdb(m, d, b or 0)

    return LinearTranslator(scale_factor=1.0, offset=offset)
