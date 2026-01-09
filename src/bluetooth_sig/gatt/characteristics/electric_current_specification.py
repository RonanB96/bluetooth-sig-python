"""Electric Current Specification characteristic implementation."""

from __future__ import annotations

import msgspec

from ...types.gatt_enums import ValueType
from ..constants import UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ElectricCurrentSpecificationData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for electric current specification."""

    minimum: float  # Minimum current in Amperes
    maximum: float  # Maximum current in Amperes

    def __post_init__(self) -> None:
        """Validate current specification data."""
        if self.minimum > self.maximum:
            raise ValueError(f"Minimum current {self.minimum} A cannot be greater than maximum {self.maximum} A")

        # Validate range for uint16 with 0.01 A resolution (0 to 655.35 A)
        max_current_value = UINT16_MAX * 0.01
        if not 0.0 <= self.minimum <= max_current_value:
            raise ValueError(f"Minimum current {self.minimum} A is outside valid range (0.0 to {max_current_value} A)")
        if not 0.0 <= self.maximum <= max_current_value:
            raise ValueError(f"Maximum current {self.maximum} A is outside valid range (0.0 to {max_current_value} A)")


class ElectricCurrentSpecificationCharacteristic(BaseCharacteristic[ElectricCurrentSpecificationData]):
    """Electric Current Specification characteristic (0x2AF0).

    org.bluetooth.characteristic.electric_current_specification

    Electric Current Specification characteristic.

    Specifies minimum and maximum current values for electrical
    specifications.
    """

    # Validation attributes
    expected_length: int = 4  # 2x uint16

    # Override since decode_value returns structured ElectricCurrentSpecificationData
    _manual_value_type: ValueType | str | None = ValueType.DICT

    def _decode_value(
        self, data: bytearray, _ctx: CharacteristicContext | None = None
    ) -> ElectricCurrentSpecificationData:
        """Parse current specification data (2x uint16 in units of 0.01 A).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            ElectricCurrentSpecificationData with 'minimum' and 'maximum' current specification values in Amperes

        Raises:
            ValueError: If data is insufficient

        """
        if len(data) < 4:
            raise ValueError("Electric current specification data must be at least 4 bytes")

        # Convert 2x uint16 (little endian) to current specification in Amperes
        min_current_raw = DataParser.parse_int16(data, 0, signed=False)
        max_current_raw = DataParser.parse_int16(data, 2, signed=False)

        return ElectricCurrentSpecificationData(minimum=min_current_raw * 0.01, maximum=max_current_raw * 0.01)

    def _encode_value(self, data: ElectricCurrentSpecificationData) -> bytearray:
        """Encode electric current specification value back to bytes.

        Args:
            data: ElectricCurrentSpecificationData instance

        Returns:
            Encoded bytes representing the current specification (2x uint16, 0.01 A resolution)

        """
        # Convert Amperes to raw values (multiply by 100 for 0.01 A resolution)
        min_current_raw = round(data.minimum * 100)
        max_current_raw = round(data.maximum * 100)

        # Encode as 2 uint16 values (little endian)
        result = bytearray()
        result.extend(DataParser.encode_int16(min_current_raw, signed=False))
        result.extend(DataParser.encode_int16(max_current_raw, signed=False))

        return result
