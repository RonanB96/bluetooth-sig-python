"""Acceleration - 3D characteristic implementation."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .templates import VectorData
from .utils import DataParser


class Acceleration3DCharacteristic(BaseCharacteristic[VectorData]):
    """Acceleration - 3D characteristic (0x2C1D).

    org.bluetooth.characteristic.acceleration_3d

    The Acceleration - 3D characteristic represents a measure of acceleration with a limited range.
    """

    _characteristic_name: str | None = "Acceleration 3D"
    resolution: float = 0.01
    _manual_value_type = "VectorData"

    # BaseCharacteristic handles validation
    expected_length = 3

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> VectorData:
        """Parse 3D acceleration (3 x sint8).

        Args:
            data: Raw bytearray from BLE characteristic (3 bytes, validated by base class).
            ctx: Optional CharacteristicContext.

        Returns:
            VectorData with x, y, z axis values in gₙ (standard acceleration due to gravity).
        """
        x_raw = DataParser.parse_int8(data, 0, signed=True)
        y_raw = DataParser.parse_int8(data, 1, signed=True)
        z_raw = DataParser.parse_int8(data, 2, signed=True)

        return VectorData(
            x_axis=x_raw * self.resolution,
            y_axis=y_raw * self.resolution,
            z_axis=z_raw * self.resolution,
        )

    def _encode_value(self, data: VectorData) -> bytearray:
        """Encode 3D acceleration.

        Args:
            data: VectorData with x, y, z axis values in gₙ.

        Returns:
            Encoded bytes (3 bytes)
        """
        x_raw = int(data.x_axis / self.resolution)
        y_raw = int(data.y_axis / self.resolution)
        z_raw = int(data.z_axis / self.resolution)

        result = bytearray()
        result.extend(DataParser.encode_int8(x_raw, signed=True))
        result.extend(DataParser.encode_int8(y_raw, signed=True))
        result.extend(DataParser.encode_int8(z_raw, signed=True))
        return result
