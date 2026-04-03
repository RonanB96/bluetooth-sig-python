"""Supported Power Range characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import SINT16_MAX, SINT16_MIN, UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class SupportedPowerRangeData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for supported power range.

    Per FTMS v1.0: Minimum Power (sint16) + Maximum Power (sint16) +
    Minimum Increment (uint16), all in Watts.
    """

    minimum: int  # Minimum power in Watts
    maximum: int  # Maximum power in Watts
    minimum_increment: int  # Minimum power increment in Watts

    def __post_init__(self) -> None:
        """Validate power range data."""
        if self.minimum > self.maximum:
            raise ValueError(f"Minimum power {self.minimum} W cannot be greater than maximum {self.maximum} W")

        if not SINT16_MIN <= self.minimum <= SINT16_MAX:
            raise ValueError(f"Minimum power {self.minimum} W is outside valid range ({SINT16_MIN} to {SINT16_MAX} W)")
        if not SINT16_MIN <= self.maximum <= SINT16_MAX:
            raise ValueError(f"Maximum power {self.maximum} W is outside valid range ({SINT16_MIN} to {SINT16_MAX} W)")
        if not 0 <= self.minimum_increment <= UINT16_MAX:
            raise ValueError(
                f"Minimum increment {self.minimum_increment} W is outside valid range (0 to {UINT16_MAX} W)"
            )


class SupportedPowerRangeCharacteristic(BaseCharacteristic[SupportedPowerRangeData]):
    """Supported Power Range characteristic (0x2AD8).

    org.bluetooth.characteristic.supported_power_range

    Specifies minimum power, maximum power, and minimum power increment
    supported by a fitness machine (FTMS v1.0).
    """

    expected_length: int = 6  # 2x sint16 + 1x uint16
    min_length: int = 6

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> SupportedPowerRangeData:
        """Parse supported power range data.

        Layout: Minimum Power (sint16) + Maximum Power (sint16) +
        Minimum Increment (uint16) = 6 bytes.
        """
        min_power_raw = DataParser.parse_int16(data, 0, signed=True)
        max_power_raw = DataParser.parse_int16(data, 2, signed=True)
        min_increment_raw = DataParser.parse_int16(data, 4, signed=False)

        return SupportedPowerRangeData(
            minimum=min_power_raw,
            maximum=max_power_raw,
            minimum_increment=min_increment_raw,
        )

    def _encode_value(self, data: SupportedPowerRangeData) -> bytearray:
        """Encode supported power range value back to bytes."""
        if not isinstance(data, SupportedPowerRangeData):
            raise TypeError(f"Supported power range data must be a SupportedPowerRangeData, got {type(data).__name__}")

        if not SINT16_MIN <= data.minimum <= SINT16_MAX:
            raise ValueError(f"Minimum power {data.minimum} exceeds sint16 range")
        if not SINT16_MIN <= data.maximum <= SINT16_MAX:
            raise ValueError(f"Maximum power {data.maximum} exceeds sint16 range")
        if not 0 <= data.minimum_increment <= UINT16_MAX:
            raise ValueError(f"Minimum increment {data.minimum_increment} exceeds uint16 range")

        result = bytearray()
        result.extend(DataParser.encode_int16(data.minimum, signed=True))
        result.extend(DataParser.encode_int16(data.maximum, signed=True))
        result.extend(DataParser.encode_int16(data.minimum_increment, signed=False))

        return result
