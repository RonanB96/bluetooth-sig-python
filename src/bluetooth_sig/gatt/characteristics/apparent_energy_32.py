"""Apparent Energy 32 characteristic implementation."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils.data_parser import DataParser


class ApparentEnergy32Characteristic(BaseCharacteristic[float]):
    """Apparent Energy 32 characteristic (0x2B89).

    org.bluetooth.characteristic.apparent_energy_32

    The Apparent Energy 32 characteristic is used to represent the integral of Apparent Power over a time interval.
    """

    _manual_unit: str | None = (
        "kVAh"  # YAML: electrical_apparent_energy.kilovolt_ampere_hour, units.yaml: energy.kilovolt_ampere_hour
    )

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> float:
        """Decode apparent energy 32 characteristic.

        Decodes a 32-bit unsigned integer representing apparent energy in 0.001 kVAh increments
        per Bluetooth SIG Apparent Energy 32 characteristic specification.

        Args:
            data: Raw bytes from BLE characteristic (exactly 4 bytes, little-endian)
            ctx: Optional context for parsing (device info, flags, etc.)
            validate: Whether to validate ranges (default True)

        Returns:
            Apparent energy in kilovolt ampere hours, or None if value is not valid or unknown

        Raises:
            InsufficientDataError: If data is not exactly 4 bytes
        """
        raw_value = DataParser.parse_int32(data, 0, signed=False)
        return raw_value * 0.001

    def _encode_value(self, data: float) -> bytearray:
        """Encode apparent energy value."""
        raw_value = int(data / 0.001)
        return DataParser.encode_int32(raw_value, signed=False)
