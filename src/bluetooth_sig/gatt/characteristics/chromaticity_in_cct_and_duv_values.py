"""Chromaticity in CCT and Duv Values characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import SINT16_MAX, SINT16_MIN, UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

# Duv resolution: M=1, d=-5, b=0 → 0.00001
_DUV_RESOLUTION = 1e-5


class ChromaticityInCCTAndDuvData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for Chromaticity in CCT and Duv Values.

    Combines Correlated Color Temperature (Kelvin) with Chromatic
    Distance from Planckian (unitless Duv).
    """

    correlated_color_temperature: int  # Kelvin (uint16, raw)
    chromaticity_distance_from_planckian: float  # Unitless Duv (sint16, scaled)

    def __post_init__(self) -> None:
        """Validate CCT and Duv data."""
        if not 0 <= self.correlated_color_temperature <= UINT16_MAX:
            raise ValueError(f"CCT {self.correlated_color_temperature} K is outside valid range (0 to {UINT16_MAX})")
        duv_min = SINT16_MIN * _DUV_RESOLUTION
        duv_max = SINT16_MAX * _DUV_RESOLUTION
        if not duv_min <= self.chromaticity_distance_from_planckian <= duv_max:
            raise ValueError(
                f"Duv {self.chromaticity_distance_from_planckian} is outside valid range ({duv_min} to {duv_max})"
            )


class ChromaticityInCCTAndDuvValuesCharacteristic(BaseCharacteristic[ChromaticityInCCTAndDuvData]):
    """Chromaticity in CCT and Duv Values characteristic (0x2AE5).

    org.bluetooth.characteristic.chromaticity_in_cct_and_duv_values

    Combines Correlated Color Temperature and Chromatic Distance from
    Planckian into a single composite characteristic.

    Field 1: CCT — uint16, raw Kelvin (references Correlated Color Temperature).
    Field 2: Duv — sint16, M=1 d=-5 b=0 (references Chromatic Distance From Planckian).
    """

    # Validation attributes
    expected_length: int = 4  # uint16 + sint16
    min_length: int = 4

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ChromaticityInCCTAndDuvData:
        """Parse CCT and Duv values.

        Args:
            data: Raw bytes from the characteristic read.
            ctx: Optional CharacteristicContext (may be None).
            validate: Whether to validate ranges (default True).

        Returns:
            ChromaticityInCCTAndDuvData with CCT and Duv fields.

        """
        cct_raw = DataParser.parse_int16(data, 0, signed=False)
        duv_raw = DataParser.parse_int16(data, 2, signed=True)

        return ChromaticityInCCTAndDuvData(
            correlated_color_temperature=cct_raw,
            chromaticity_distance_from_planckian=duv_raw * _DUV_RESOLUTION,
        )

    def _encode_value(self, data: ChromaticityInCCTAndDuvData) -> bytearray:
        """Encode CCT and Duv values to bytes.

        Args:
            data: ChromaticityInCCTAndDuvData instance.

        Returns:
            Encoded bytes (uint16 + sint16, little-endian).

        """
        if not isinstance(data, ChromaticityInCCTAndDuvData):
            raise TypeError(f"Expected ChromaticityInCCTAndDuvData, got {type(data).__name__}")

        cct_raw = data.correlated_color_temperature
        duv_raw = round(data.chromaticity_distance_from_planckian / _DUV_RESOLUTION)

        if not 0 <= cct_raw <= UINT16_MAX:
            raise ValueError(f"CCT raw value {cct_raw} exceeds uint16 range")
        if not SINT16_MIN <= duv_raw <= SINT16_MAX:
            raise ValueError(f"Duv raw value {duv_raw} exceeds sint16 range")

        result = bytearray()
        result.extend(DataParser.encode_int16(cct_raw, signed=False))
        result.extend(DataParser.encode_int16(duv_raw, signed=True))
        return result
