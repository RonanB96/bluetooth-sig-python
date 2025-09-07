"""Illuminance characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic

# pylint: disable=duplicate-code
# Justification: This file follows the standard BLE characteristic base class pattern,
# which is intentionally duplicated across multiple characteristic implementations.
# These patterns are required by Bluetooth SIG specifications and represent legitimate
# code duplication for protocol compliance.


@dataclass
class IlluminanceCharacteristic(BaseCharacteristic):
    """Illuminance characteristic (0x2AFB).

    Measures light intensity in lux (lumens per square meter).
    """

    _characteristic_name: str = "Illuminance"

    def parse_value(self, data: bytearray) -> float:
        """Parse illuminance data.

        Format: 3-byte value representing illuminance in 0.01 lux units.

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Illuminance value in lux
        """
        if len(data) < 3:
            raise ValueError("Illuminance data must be at least 3 bytes")

        # Convert 3-byte unsigned integer (little endian) to illuminance in lux
        illuminance_raw = int.from_bytes(data[:3], byteorder="little", signed=False)
        return illuminance_raw * 0.01

    def encode_value(self, data: float | int) -> bytearray:
        """Encode illuminance value back to bytes.

        Args:
            data: Illuminance value in lux

        Returns:
            Encoded bytes representing the illuminance (uint24, 0.01 lx resolution)
        """
        illuminance = float(data)

        # Validate range (reasonable illuminance range)
        if not 0.0 <= illuminance <= 167772.15:  # Max uint24 * 0.01
            raise ValueError(
                f"Illuminance {illuminance} lx is outside valid range (0.0 to 167772.15 lx)"
            )

        # Convert lux to raw value (multiply by 100 for 0.01 lx resolution)
        illuminance_raw = round(illuminance * 100)

        # Ensure it fits in uint24
        if illuminance_raw > 0xFFFFFF:  # pylint: disable=consider-using-min-builtin # Clear intent for range clamping
            illuminance_raw = 0xFFFFFF

        # Encode as 3 bytes (little endian)
        return bytearray(illuminance_raw.to_bytes(3, byteorder="little", signed=False))

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "lx"
