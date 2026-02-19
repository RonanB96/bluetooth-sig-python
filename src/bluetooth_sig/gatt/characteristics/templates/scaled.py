"""Scaled value templates with configurable resolution and offset.

Covers ScaledTemplate (abstract), ScaledUint8/16/24/32, ScaledSint8/16/24/32,
and PercentageTemplate.
"""

from __future__ import annotations

from abc import abstractmethod

from ...constants import (
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
from ...context import CharacteristicContext
from ...exceptions import InsufficientDataError, ValueRangeError
from ..utils.extractors import (
    SINT8,
    SINT16,
    SINT24,
    SINT32,
    UINT8,
    UINT16,
    UINT24,
    UINT32,
    RawExtractor,
)
from ..utils.translators import (
    IDENTITY,
    IdentityTranslator,
    LinearTranslator,
)
from .base import CodingTemplate


class ScaledTemplate(CodingTemplate[float]):
    """Base class for scaled integer templates.

    Handles common scaling logic: value = (raw + offset) * scale_factor
    Subclasses implement raw parsing/encoding and range checking.

    Exposes `extractor` and `translator` for pipeline access.
    """

    _extractor: RawExtractor
    _translator: LinearTranslator

    def __init__(self, scale_factor: float, offset: int) -> None:
        """Initialize with scale factor and offset.

        Args:
            scale_factor: Factor to multiply raw value by
            offset: Offset to add to raw value before scaling

        """
        self._translator = LinearTranslator(scale_factor=scale_factor, offset=offset)

    @property
    def scale_factor(self) -> float:
        """Get the scale factor."""
        return self._translator.scale_factor

    @property
    def offset(self) -> int:
        """Get the offset."""
        return self._translator.offset

    @property
    def extractor(self) -> RawExtractor:
        """Get the byte extractor for pipeline access."""
        return self._extractor

    @property
    def translator(self) -> LinearTranslator:
        """Get the value translator for pipeline access."""
        return self._translator

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> float:
        """Parse scaled integer value."""
        raw_value = self._extractor.extract(data, offset)
        return self._translator.translate(raw_value)

    def encode_value(self, value: float, *, validate: bool = True) -> bytearray:
        """Encode scaled value to bytes."""
        raw_value = self._translator.untranslate(value)
        if validate:
            self._check_range(raw_value)
        return self._extractor.pack(raw_value)

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
            ScaledTemplate instance

        """
        return cls(scale_factor=scale_factor, offset=offset)

    @classmethod
    def from_letter_method(cls, M: int, d: int, b: int) -> ScaledTemplate:  # noqa: N803
        """Create instance using Bluetooth SIG M, d, b parameters.

        Args:
            M: Multiplier factor
            d: Decimal exponent (10^d)
            b: Offset to add to raw value before scaling

        Returns:
            ScaledTemplate instance

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

    _extractor = UINT16

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

    _extractor = SINT16

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

    _extractor = SINT8

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

    _extractor = UINT8

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

    def _check_range(self, raw: int) -> None:
        """Check range for uint8."""
        if not 0 <= raw <= UINT8_MAX:
            raise ValueError(f"Scaled value {raw} out of range for uint8")


class ScaledUint32Template(ScaledTemplate):
    """Template for scaled 32-bit unsigned integer with configurable resolution and offset."""

    _extractor = UINT32

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

    def _check_range(self, raw: int) -> None:
        """Check range for uint32."""
        if not 0 <= raw <= UINT32_MAX:
            raise ValueError(f"Scaled value {raw} out of range for uint32")


class ScaledUint24Template(ScaledTemplate):
    """Template for scaled 24-bit unsigned integer with configurable resolution and offset.

    Used for values encoded in 3 bytes as unsigned integers.
    Example: Illuminance 1000 lux stored as bytes with scale_factor=1.0, offset=0
    """

    _extractor = UINT24

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

    def _check_range(self, raw: int) -> None:
        """Check range for uint24."""
        if not 0 <= raw <= UINT24_MAX:
            raise ValueError(f"Scaled value {raw} out of range for uint24")


class ScaledSint24Template(ScaledTemplate):
    """Template for scaled 24-bit signed integer with configurable resolution and offset.

    Used for signed values encoded in 3 bytes.
    Example: Elevation 500.00m stored as bytes with scale_factor=0.01, offset=0
    """

    _extractor = SINT24

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

    def _check_range(self, raw: int) -> None:
        """Check range for sint24."""
        if not SINT24_MIN <= raw <= SINT24_MAX:
            raise ValueError(f"Scaled value {raw} out of range for sint24")


class ScaledSint32Template(ScaledTemplate):
    """Template for scaled 32-bit signed integer with configurable resolution and offset.

    Used for signed values encoded in 4 bytes.
    Example: Longitude -180.0 to 180.0 degrees stored with scale_factor=1e-7
    """

    _extractor = SINT32

    def __init__(self, scale_factor: float = 0.01, offset: int = 0) -> None:
        """Initialize with scale factor and offset.

        Args:
            scale_factor: Factor to multiply raw value by
            offset: Offset to add to raw value before scaling

        """
        super().__init__(scale_factor, offset)

    @property
    def data_size(self) -> int:
        """Size: 4 bytes."""
        return 4

    def _check_range(self, raw: int) -> None:
        """Check range for sint32."""
        sint32_min = -(2**31)
        sint32_max = (2**31) - 1
        if not sint32_min <= raw <= sint32_max:
            raise ValueError(f"Scaled value {raw} out of range for sint32")


class PercentageTemplate(CodingTemplate[int]):
    """Template for percentage values (0-100%) using uint8."""

    @property
    def data_size(self) -> int:
        """Size: 1 byte."""
        return 1

    @property
    def extractor(self) -> RawExtractor:
        """Get uint8 extractor."""
        return UINT8

    @property
    def translator(self) -> IdentityTranslator:
        """Return identity translator since validation is separate from translation."""
        return IDENTITY

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> int:
        """Parse percentage value."""
        if validate and len(data) < offset + 1:
            raise InsufficientDataError("percentage", data[offset:], 1)
        value = self.extractor.extract(data, offset)
        # Only validate range if validation is enabled
        if validate and not 0 <= value <= PERCENTAGE_MAX:
            raise ValueRangeError("percentage", value, 0, PERCENTAGE_MAX)
        return self.translator.translate(value)

    def encode_value(self, value: int, *, validate: bool = True) -> bytearray:
        """Encode percentage value to bytes."""
        if validate and not 0 <= value <= PERCENTAGE_MAX:
            raise ValueError(f"Percentage value {value} out of range (0-{PERCENTAGE_MAX})")
        raw = self.translator.untranslate(value)
        return self.extractor.pack(raw)
