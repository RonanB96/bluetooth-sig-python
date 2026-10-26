"""Supported Heart Rate Range characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import UINT8_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class SupportedHeartRateRangeData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for supported heart rate range.

    All values are in beats per minute (BPM), integer precision.
    """

    minimum: int  # Minimum heart rate in BPM
    maximum: int  # Maximum heart rate in BPM
    minimum_increment: int  # Minimum increment in BPM

    def __post_init__(self) -> None:
        """Validate heart rate range data."""
        if self.minimum > self.maximum:
            raise ValueError(f"Minimum heart rate {self.minimum} BPM cannot be greater than maximum {self.maximum} BPM")
        for name, val in [
            ("minimum", self.minimum),
            ("maximum", self.maximum),
            ("minimum_increment", self.minimum_increment),
        ]:
            if not 0 <= val <= UINT8_MAX:
                raise ValueError(f"{name} {val} BPM is outside valid range (0 to {UINT8_MAX})")


class SupportedHeartRateRangeCharacteristic(BaseCharacteristic[SupportedHeartRateRangeData]):
    """Supported Heart Rate Range characteristic (0x2AD7).

    org.bluetooth.characteristic.supported_heart_rate_range

    Represents the heart rate range supported by a fitness machine.
    Three fields: minimum heart rate, maximum heart rate, and minimum
    increment. Each is a uint8 in beats per minute (no scaling).
    """

    # Validation attributes
    expected_length: int = 3  # 3 x uint8
    min_length: int = 3

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> SupportedHeartRateRangeData:
        """Parse supported heart rate range data.

        Args:
            data: Raw bytes from the characteristic read.
            ctx: Optional CharacteristicContext (may be None).
            validate: Whether to validate ranges (default True).

        Returns:
            SupportedHeartRateRangeData with minimum, maximum, and increment.

        """
        min_raw = DataParser.parse_int8(data, 0, signed=False)
        max_raw = DataParser.parse_int8(data, 1, signed=False)
        inc_raw = DataParser.parse_int8(data, 2, signed=False)

        return SupportedHeartRateRangeData(
            minimum=min_raw,
            maximum=max_raw,
            minimum_increment=inc_raw,
        )

    def _encode_value(self, data: SupportedHeartRateRangeData) -> bytearray:
        """Encode supported heart rate range to bytes.

        Args:
            data: SupportedHeartRateRangeData instance.

        Returns:
            Encoded bytes (3 x uint8).

        """
        if not isinstance(data, SupportedHeartRateRangeData):
            raise TypeError(f"Expected SupportedHeartRateRangeData, got {type(data).__name__}")

        result = bytearray()
        result.extend(DataParser.encode_int8(data.minimum, signed=False))
        result.extend(DataParser.encode_int8(data.maximum, signed=False))
        result.extend(DataParser.encode_int8(data.minimum_increment, signed=False))
        return result
