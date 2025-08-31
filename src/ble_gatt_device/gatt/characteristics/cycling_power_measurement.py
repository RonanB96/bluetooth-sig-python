"""Cycling Power Measurement characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any, Dict

from .base import BaseCharacteristic


@dataclass
class CyclingPowerMeasurementCharacteristic(BaseCharacteristic):
    """Cycling Power Measurement characteristic (0x2A63).

    Used to transmit cycling power measurement data including instantaneous power,
    pedal power balance, accumulated energy, and revolution data.
    """

    _characteristic_name: str = "Cycling Power Measurement"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "string"  # JSON string representation
        super().__post_init__()

    def parse_value(self, data: bytearray) -> Dict[str, Any]:
        """Parse cycling power measurement data according to Bluetooth specification.

        Format: Flags(2) + Instantaneous Power(2) + [Pedal Power Balance(1)] + 
        [Accumulated Energy(2)] + [Wheel Revolutions(4)] + [Last Wheel Event Time(2)] + 
        [Crank Revolutions(2)] + [Last Crank Event Time(2)]

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Dict containing parsed cycling power data with metadata

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 4:
            raise ValueError("Cycling Power Measurement data must be at least 4 bytes")

        # Parse flags (16-bit)
        flags = struct.unpack("<H", data[:2])[0]
        
        # Parse instantaneous power (16-bit signed integer in watts)
        instantaneous_power = struct.unpack("<h", data[2:4])[0]
        
        result = {
            "flags": flags,
            "instantaneous_power": instantaneous_power,
            "unit": "W"
        }

        offset = 4

        # Parse optional pedal power balance (1 byte) if present
        if (flags & 0x0001) and len(data) >= offset + 1:
            pedal_power_balance = data[offset]
            # Value 0xFF indicates unknown, otherwise percentage (0-100)
            if pedal_power_balance != 0xFF:
                result["pedal_power_balance"] = pedal_power_balance / 2.0  # 0.5% resolution
            offset += 1

        # Parse optional accumulated energy (2 bytes) if present
        if (flags & 0x0008) and len(data) >= offset + 2:
            accumulated_energy = struct.unpack("<H", data[offset:offset + 2])[0]
            result["accumulated_energy"] = accumulated_energy  # kJ
            offset += 2

        # Parse optional wheel revolution data (6 bytes total) if present
        if (flags & 0x0010) and len(data) >= offset + 6:
            wheel_revolutions = struct.unpack("<I", data[offset:offset + 4])[0]
            wheel_event_time_raw = struct.unpack("<H", data[offset + 4:offset + 6])[0]
            # Wheel event time is in 1/2048 second units
            wheel_event_time = wheel_event_time_raw / 2048.0

            result.update({
                "cumulative_wheel_revolutions": wheel_revolutions,
                "last_wheel_event_time": wheel_event_time,
            })
            offset += 6

        # Parse optional crank revolution data (4 bytes total) if present
        if (flags & 0x0020) and len(data) >= offset + 4:
            crank_revolutions = struct.unpack("<H", data[offset:offset + 2])[0]
            crank_event_time_raw = struct.unpack("<H", data[offset + 2:offset + 4])[0]
            # Crank event time is in 1/1024 second units
            crank_event_time = crank_event_time_raw / 1024.0

            result.update({
                "cumulative_crank_revolutions": crank_revolutions,
                "last_crank_event_time": crank_event_time,
            })
            offset += 4

        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "W"  # Watts

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "power"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "measurement"