"""Electric Current Range characteristic implementation."""

from __future__ import annotations

import msgspec

from ...types.gatt_enums import ValueType
from ..constants import UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ElectricCurrentRangeData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for electric current range."""

    min: float  # Minimum current in Amperes
    max: float  # Maximum current in Amperes

    def __post_init__(self) -> None:
        """Validate current range data."""
        if self.min > self.max:
            raise ValueError(f"Minimum current {self.min} A cannot be greater than maximum {self.max} A")

        # Validate range for uint16 with 0.01 A resolution (0 to 655.35 A)
        max_current_value = UINT16_MAX * 0.01
        if not 0.0 <= self.min <= max_current_value:
            raise ValueError(f"Minimum current {self.min} A is outside valid range (0.0 to {max_current_value} A)")
        if not 0.0 <= self.max <= max_current_value:
            raise ValueError(f"Maximum current {self.max} A is outside valid range (0.0 to {max_current_value} A)")


class ElectricCurrentRangeCharacteristic(BaseCharacteristic[ElectricCurrentRangeData]):
    """Electric Current Range characteristic (0x2AEF).

    org.bluetooth.characteristic.electric_current_range

    Electric Current Range characteristic.

    Specifies lower and upper current bounds (2x uint16).
    """

    # Validation attributes
    expected_length: int = 4  # 2x uint16

    # Override since decode_value returns structured ElectricCurrentRangeData
    _manual_value_type: ValueType | str | None = ValueType.DICT

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ElectricCurrentRangeData:
        """Parse current range data (2x uint16 in units of 0.01 A).

        Args:
            data: Raw bytes from the characteristic read.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            ElectricCurrentRangeData with 'min' and 'max' current values in Amperes.

        Raises:
            ValueError: If data is insufficient.

        """
        if len(data) < 4:
            raise ValueError("Electric current range data must be at least 4 bytes")

        # Convert 2x uint16 (little endian) to current range in Amperes
        min_current_raw = DataParser.parse_int16(data, 0, signed=False)
        max_current_raw = DataParser.parse_int16(data, 2, signed=False)

        return ElectricCurrentRangeData(min=min_current_raw * 0.01, max=max_current_raw * 0.01)

    def _encode_value(self, data: ElectricCurrentRangeData) -> bytearray:
        """Encode electric current range value back to bytes.

        Args:
            data: ElectricCurrentRangeData instance with 'min' and 'max' current values in Amperes

        Returns:
            Encoded bytes representing the current range (2x uint16, 0.01 A resolution)

        """
        if not isinstance(data, ElectricCurrentRangeData):
            raise TypeError(
                f"Electric current range data must be an ElectricCurrentRangeData, got {type(data).__name__}"
            )
            # Convert Amperes to raw values (multiply by 100 for 0.01 A resolution)
        min_current_raw = round(data.min * 100)
        max_current_raw = round(data.max * 100)

        # Validate range for uint16 (0 to UINT16_MAX)
        for name, value in [("minimum", min_current_raw), ("maximum", max_current_raw)]:
            if not 0 <= value <= UINT16_MAX:
                raise ValueError(f"Current {name} value {value} exceeds uint16 range")

        # Encode as 2 uint16 values (little endian)
        result = bytearray()
        result.extend(DataParser.encode_int16(min_current_raw, signed=False))
        result.extend(DataParser.encode_int16(max_current_raw, signed=False))

        return result
