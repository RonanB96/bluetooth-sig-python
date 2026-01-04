"""Power Specification characteristic implementation."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils.data_parser import DataParser

# Special value constants for Power Specification characteristic
VALUE_NOT_VALID = 0xFFFFFE  # Indicates value is not valid
VALUE_UNKNOWN = 0xFFFFFF  # Indicates value is not known


class PowerSpecificationData:
    """Data class for Power Specification characteristic."""

    def __init__(
        self,
        minimum: float | None,
        typical: float | None,
        maximum: float | None,
    ) -> None:
        """Initialize Power Specification data.

        Args:
            minimum: Minimum power value in watts, or None if not valid/known
            typical: Typical power value in watts, or None if not valid/known
            maximum: Maximum power value in watts, or None if not valid/known
        """
        self.minimum = minimum
        self.typical = typical
        self.maximum = maximum

    def __eq__(self, other: object) -> bool:
        """Check equality with another PowerSpecificationData."""
        if not isinstance(other, PowerSpecificationData):
            return NotImplemented
        return self.minimum == other.minimum and self.typical == other.typical and self.maximum == other.maximum

    def __repr__(self) -> str:
        """Return string representation."""
        return f"PowerSpecificationData(minimum={self.minimum}, typical={self.typical}, maximum={self.maximum})"


class PowerSpecificationCharacteristic(BaseCharacteristic[PowerSpecificationData]):
    """Power Specification characteristic (0x2B06).

    org.bluetooth.characteristic.power_specification

    The Power Specification characteristic is used to represent a specification of power values.
    """

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> PowerSpecificationData:
        """Decode the power specification values."""
        # Parse three uint24 values (little-endian)
        minimum_raw = DataParser.parse_int24(data, 0, signed=False)
        typical_raw = DataParser.parse_int24(data, 3, signed=False)
        maximum_raw = DataParser.parse_int24(data, 6, signed=False)

        # Convert to float values with 0.1 W resolution, handling special values
        def _convert_value(raw: int) -> float | None:
            if raw == VALUE_NOT_VALID:
                return None  # Value is not valid
            if raw == VALUE_UNKNOWN:
                return None  # Value is not known
            return raw * 0.1  # Resolution 0.1 W

        return PowerSpecificationData(
            minimum=_convert_value(minimum_raw),
            typical=_convert_value(typical_raw),
            maximum=_convert_value(maximum_raw),
        )

    def _encode_value(self, data: PowerSpecificationData) -> bytearray:  # noqa: D202
        """Encode the power specification values."""

        # Convert float values to uint24 with 0.1 W resolution, handling special values
        def _convert_to_raw(value: float | None) -> int:
            # NOTE: D202 disabled on method - blank line required by black formatter for nested function
            if value is None:
                return VALUE_UNKNOWN  # Use "not known" as default for None
            return round(value / 0.1)

        minimum_raw = _convert_to_raw(data.minimum)
        typical_raw = _convert_to_raw(data.typical)
        maximum_raw = _convert_to_raw(data.maximum)

        # Encode three uint24 values (little-endian)
        result = bytearray()
        result.extend(DataParser.encode_int24(minimum_raw, signed=False))
        result.extend(DataParser.encode_int24(typical_raw, signed=False))
        result.extend(DataParser.encode_int24(maximum_raw, signed=False))
        return result
