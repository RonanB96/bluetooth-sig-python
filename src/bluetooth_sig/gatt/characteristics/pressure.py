"""Pressure characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class PressureCharacteristic(BaseCharacteristic):
    """Atmospheric pressure characteristic."""

    _characteristic_name: str = "Pressure"

    def parse_value(self, data: bytearray) -> float:
        """Parse pressure data (uint32 in units of 0.1 Pa)."""
        if len(data) < 4:
            raise ValueError("Pressure data must be at least 4 bytes")

        # Convert uint32 (little endian) to pressure in Pa
        pressure_raw = int.from_bytes(data[:4], byteorder="little", signed=False)
        return pressure_raw * 0.1  # Convert to Pa with 0.1 Pa resolution

    def encode_value(self, data: float | int) -> bytearray:
        """Encode pressure value back to bytes.

        Args:
            data: Pressure value in Pa

        Returns:
            Encoded bytes representing the pressure (uint32, 0.1 Pa resolution)
        """
        pressure_pa = float(data)

        # Validate range (reasonable atmospheric pressure range)
        if not 0 <= pressure_pa <= 200000:  # 0 to 2000 hPa (200000 Pa)
            raise ValueError(
                f"Pressure {pressure_pa} Pa is outside valid range (0-200000 Pa)"
            )

        # Convert Pa to raw value (divide by 0.1 for 0.1 Pa resolution)
        pressure_raw = round(pressure_pa / 0.1)

        # Ensure it fits in uint32
        if pressure_raw > 0xFFFFFFFF:
            raise ValueError(f"Pressure value {pressure_raw} exceeds uint32 range")

        return bytearray(pressure_raw.to_bytes(4, byteorder="little", signed=False))
