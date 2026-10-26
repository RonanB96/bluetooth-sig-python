"""Luminous Flux Range characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class LuminousFluxRangeData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for luminous flux range.

    Each value is a luminous flux in lumens (resolution 1 lm).
    """

    minimum: int  # Minimum luminous flux in lumens
    maximum: int  # Maximum luminous flux in lumens

    def __post_init__(self) -> None:
        """Validate luminous flux range data."""
        if self.minimum > self.maximum:
            raise ValueError(
                f"Minimum luminous flux {self.minimum} lm cannot be greater than maximum {self.maximum} lm"
            )
        for name, val in [("minimum", self.minimum), ("maximum", self.maximum)]:
            if not 0 <= val <= UINT16_MAX:
                raise ValueError(
                    f"{name.capitalize()} luminous flux {val} lm is outside valid range (0 to {UINT16_MAX})"
                )


class LuminousFluxRangeCharacteristic(BaseCharacteristic[LuminousFluxRangeData]):
    """Luminous Flux Range characteristic (0x2B00).

    org.bluetooth.characteristic.luminous_flux_range

    Represents a luminous flux range as a pair of Luminous Flux values.
    Each field is a uint16 with resolution 1 lumen.
    """

    # Validation attributes
    expected_length: int = 4  # 2 x uint16
    min_length: int = 4

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> LuminousFluxRangeData:
        """Parse luminous flux range data (2 x uint16, resolution 1 lm).

        Args:
            data: Raw bytes from the characteristic read.
            ctx: Optional CharacteristicContext (may be None).
            validate: Whether to validate ranges (default True).

        Returns:
            LuminousFluxRangeData with minimum and maximum luminous flux in lumens.

        """
        min_raw = DataParser.parse_int16(data, 0, signed=False)
        max_raw = DataParser.parse_int16(data, 2, signed=False)

        return LuminousFluxRangeData(minimum=min_raw, maximum=max_raw)

    def _encode_value(self, data: LuminousFluxRangeData) -> bytearray:
        """Encode luminous flux range to bytes.

        Args:
            data: LuminousFluxRangeData instance.

        Returns:
            Encoded bytes (2 x uint16, little-endian).

        """
        if not isinstance(data, LuminousFluxRangeData):
            raise TypeError(f"Expected LuminousFluxRangeData, got {type(data).__name__}")

        for name, value in [("minimum", data.minimum), ("maximum", data.maximum)]:
            if not 0 <= value <= UINT16_MAX:
                raise ValueError(f"Luminous flux {name} value {value} exceeds uint16 range")

        result = bytearray()
        result.extend(DataParser.encode_int16(data.minimum, signed=False))
        result.extend(DataParser.encode_int16(data.maximum, signed=False))
        return result
