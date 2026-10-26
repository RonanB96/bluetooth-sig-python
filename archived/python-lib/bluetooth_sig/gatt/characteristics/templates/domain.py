"""Domain-specific templates that compose scaled templates.

Covers TemperatureTemplate, ConcentrationTemplate, PressureTemplate.
"""

from __future__ import annotations

from ...context import CharacteristicContext
from ..utils.extractors import RawExtractor
from ..utils.translators import ValueTranslator
from .base import _RESOLUTION_HUNDREDTH, _RESOLUTION_INTEGER, _RESOLUTION_TENTH, CodingTemplate
from .scaled import ScaledSint16Template, ScaledUint16Template, ScaledUint32Template


class TemperatureTemplate(CodingTemplate[float]):
    """Template for standard Bluetooth SIG temperature format (sint16, 0.01°C resolution)."""

    def __init__(self) -> None:
        """Initialize with standard temperature resolution."""
        self._scaled_template = ScaledSint16Template.from_letter_method(1, -2, 0)

    @property
    def data_size(self) -> int:
        """Size: 2 bytes."""
        return 2

    @property
    def extractor(self) -> RawExtractor:
        """Get extractor from underlying scaled template."""
        return self._scaled_template.extractor

    @property
    def translator(self) -> ValueTranslator[float]:
        """Return the linear translator from the underlying scaled template."""
        return self._scaled_template.translator

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> float:
        """Parse temperature in 0.01°C resolution."""
        return self._scaled_template.decode_value(data, offset, ctx, validate=validate)  # pylint: disable=protected-access

    def encode_value(self, value: float, *, validate: bool = True) -> bytearray:
        """Encode temperature to bytes."""
        return self._scaled_template.encode_value(value, validate=validate)  # pylint: disable=protected-access


class ConcentrationTemplate(CodingTemplate[float]):
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
        if resolution == _RESOLUTION_INTEGER:
            # resolution = 1 * 10^0  # noqa: ERA001
            self._scaled_template = ScaledUint16Template.from_letter_method(M=1, d=0, b=0)
        elif resolution == _RESOLUTION_TENTH:
            # resolution = 1 * 10^-1  # noqa: ERA001
            self._scaled_template = ScaledUint16Template.from_letter_method(M=1, d=-1, b=0)
        elif resolution == _RESOLUTION_HUNDREDTH:
            # resolution = 1 * 10^-2  # noqa: ERA001
            self._scaled_template = ScaledUint16Template.from_letter_method(M=1, d=-2, b=0)
        else:
            # Fallback to scale_factor for resolutions that don't fit M * 10^d pattern
            self._scaled_template = ScaledUint16Template(scale_factor=resolution)

    @classmethod
    def from_letter_method(cls, M: int, d: int, b: int = 0) -> ConcentrationTemplate:  # noqa: N803
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

    @property
    def extractor(self) -> RawExtractor:
        """Get extractor from underlying scaled template."""
        return self._scaled_template.extractor

    @property
    def translator(self) -> ValueTranslator[float]:
        """Return the linear translator from the underlying scaled template."""
        return self._scaled_template.translator

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> float:
        """Parse concentration with resolution."""
        return self._scaled_template.decode_value(data, offset, ctx, validate=validate)  # pylint: disable=protected-access

    def encode_value(self, value: float, *, validate: bool = True) -> bytearray:
        """Encode concentration value to bytes."""
        return self._scaled_template.encode_value(value, validate=validate)  # pylint: disable=protected-access


class PressureTemplate(CodingTemplate[float]):
    """Template for pressure measurements (uint32, 0.1 Pa resolution)."""

    def __init__(self) -> None:
        """Initialize with standard pressure resolution (0.1 Pa)."""
        self._scaled_template = ScaledUint32Template(scale_factor=0.1)

    @property
    def data_size(self) -> int:
        """Size: 4 bytes."""
        return 4

    @property
    def extractor(self) -> RawExtractor:
        """Get extractor from underlying scaled template."""
        return self._scaled_template.extractor

    @property
    def translator(self) -> ValueTranslator[float]:
        """Return the linear translator from the underlying scaled template."""
        return self._scaled_template.translator

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> float:
        """Parse pressure in 0.1 Pa resolution (returns Pa)."""
        return self._scaled_template.decode_value(data, offset, ctx, validate=validate)  # pylint: disable=protected-access

    def encode_value(self, value: float, *, validate: bool = True) -> bytearray:
        """Encode pressure to bytes."""
        return self._scaled_template.encode_value(value, validate=validate)  # pylint: disable=protected-access
