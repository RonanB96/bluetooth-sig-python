"""Precise Acceleration 3D characteristic implementation."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .templates import VectorData
from .utils import DataParser

_RESOLUTION = 0.001  # M=1, d=-3, b=0 -> 0.001 standard gravity


class PreciseAcceleration3DCharacteristic(BaseCharacteristic[VectorData]):
    """Precise Acceleration 3D characteristic (0x2C1E).

    org.bluetooth.characteristic.precise_acceleration_3d

    Represents a precise 3D acceleration measurement in standard gravity.
    Three fields: x, y, z (sint16 each, 0.001 gn resolution).
    """

    _characteristic_name: str | None = "Precise Acceleration 3D"
    resolution: float = _RESOLUTION
    expected_length: int = 6  # 3 x sint16
    min_length: int = 6

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> VectorData:
        """Parse precise 3D acceleration (3 x sint16).

        Args:
            data: Raw bytes (6 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            VectorData with x, y, z axis values in gn (standard gravity).

        """
        x_raw = DataParser.parse_int16(data, 0, signed=True)
        y_raw = DataParser.parse_int16(data, 2, signed=True)
        z_raw = DataParser.parse_int16(data, 4, signed=True)

        return VectorData(
            x_axis=x_raw * _RESOLUTION,
            y_axis=y_raw * _RESOLUTION,
            z_axis=z_raw * _RESOLUTION,
        )

    def _encode_value(self, data: VectorData) -> bytearray:
        """Encode precise 3D acceleration.

        Args:
            data: VectorData with x, y, z axis values in gn.

        Returns:
            Encoded bytes (6 bytes).

        """
        x_raw = round(data.x_axis / _RESOLUTION)
        y_raw = round(data.y_axis / _RESOLUTION)
        z_raw = round(data.z_axis / _RESOLUTION)

        result = bytearray()
        result.extend(DataParser.encode_int16(x_raw, signed=True))
        result.extend(DataParser.encode_int16(y_raw, signed=True))
        result.extend(DataParser.encode_int16(z_raw, signed=True))
        return result
