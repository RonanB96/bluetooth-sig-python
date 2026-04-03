"""Electric Current Specification characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_CURRENT_RESOLUTION = 0.01  # 0.01 A per raw unit
_MAX_CURRENT = UINT16_MAX * _CURRENT_RESOLUTION  # 655.35 A


class ElectricCurrentSpecificationData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for electric current specification.

    Three current values (0.01 A resolution): Minimum, Typical, Maximum.
    """

    minimum: float  # Minimum current in Amperes
    typical: float  # Typical current in Amperes
    maximum: float  # Maximum current in Amperes

    def __post_init__(self) -> None:
        """Validate current specification data."""
        if self.minimum > self.maximum:
            raise ValueError(f"Minimum current {self.minimum} A cannot be greater than maximum {self.maximum} A")

        for name, current in [
            ("minimum", self.minimum),
            ("typical", self.typical),
            ("maximum", self.maximum),
        ]:
            if not 0.0 <= current <= _MAX_CURRENT:
                raise ValueError(
                    f"{name.capitalize()} current {current} A is outside valid range (0.0 to {_MAX_CURRENT} A)"
                )


class ElectricCurrentSpecificationCharacteristic(BaseCharacteristic[ElectricCurrentSpecificationData]):
    """Electric Current Specification characteristic (0x2AF0).

    org.bluetooth.characteristic.electric_current_specification

    Specifies minimum, typical, and maximum current values (uint16, 0.01 A resolution).
    """

    expected_length: int = 6  # 3x uint16
    min_length: int = 6

    def _decode_value(
        self, data: bytearray, _ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ElectricCurrentSpecificationData:
        """Parse current specification data (3x uint16 in units of 0.01 A)."""
        min_current_raw = DataParser.parse_int16(data, 0, signed=False)
        typical_current_raw = DataParser.parse_int16(data, 2, signed=False)
        max_current_raw = DataParser.parse_int16(data, 4, signed=False)

        return ElectricCurrentSpecificationData(
            minimum=min_current_raw * _CURRENT_RESOLUTION,
            typical=typical_current_raw * _CURRENT_RESOLUTION,
            maximum=max_current_raw * _CURRENT_RESOLUTION,
        )

    def _encode_value(self, data: ElectricCurrentSpecificationData) -> bytearray:
        """Encode electric current specification value back to bytes."""
        min_current_raw = round(data.minimum * 100)
        typical_current_raw = round(data.typical * 100)
        max_current_raw = round(data.maximum * 100)

        for name, value in [
            ("minimum", min_current_raw),
            ("typical", typical_current_raw),
            ("maximum", max_current_raw),
        ]:
            if not 0 <= value <= UINT16_MAX:
                raise ValueError(f"Current {name} value {value} exceeds uint16 range")

        result = bytearray()
        result.extend(DataParser.encode_int16(min_current_raw, signed=False))
        result.extend(DataParser.encode_int16(typical_current_raw, signed=False))
        result.extend(DataParser.encode_int16(max_current_raw, signed=False))

        return result
