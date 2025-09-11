"""Cycling Power Measurement characteristic implementation."""

from __future__ import annotations

import struct
from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class CyclingPowerMeasurementData:  # pylint: disable=too-many-instance-attributes # Comprehensive power measurement with many optional fields
    """Parsed data from Cycling Power Measurement characteristic."""

    flags: int
    instantaneous_power: int  # Watts
    pedal_power_balance: int | None = None
    accumulated_energy: int | None = None  # kJ
    cumulative_wheel_revolutions: int | None = None  # Changed to match decode_value
    last_wheel_event_time: float | None = None  # seconds
    cumulative_crank_revolutions: int | None = None  # Changed to match decode_value
    last_crank_event_time: float | None = None  # seconds

    def __post_init__(self) -> None:
        """Validate cycling power measurement data."""
        if not 0 <= self.flags <= 65535:
            raise ValueError("Flags must be a uint16 value (0-65535)")
        if not 0 <= self.instantaneous_power <= 65535:
            raise ValueError("Instantaneous power must be a uint16 value (0-65535)")


@dataclass
class CyclingPowerMeasurementCharacteristic(BaseCharacteristic):
    """Cycling Power Measurement characteristic (0x2A63).

    Used to transmit cycling power measurement data including instantaneous power,
    pedal power balance, accumulated energy, and revolution data.
    """

    _characteristic_name: str = "Cycling Power Measurement"

    def decode_value(self, data: bytearray) -> CyclingPowerMeasurementData:
        """Parse cycling power measurement data according to Bluetooth specification.

        Format: Flags(2) + Instantaneous Power(2) + [Pedal Power Balance(1)] +
        [Accumulated Energy(2)] + [Wheel Revolutions(4)] + [Last Wheel Event Time(2)] +
        [Crank Revolutions(2)] + [Last Crank Event Time(2)]

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            CyclingPowerMeasurementData containing parsed power measurement data

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
            "unit": "W",
        }

        offset = 4

        # Parse optional pedal power balance (1 byte) if present
        if (flags & 0x0001) and len(data) >= offset + 1:
            pedal_power_balance = data[offset]
            # Value 0xFF indicates unknown, otherwise percentage (0-100)
            if pedal_power_balance != 0xFF:
                result["pedal_power_balance"] = (
                    pedal_power_balance / 2.0
                )  # 0.5% resolution
            offset += 1

        # Parse optional accumulated energy (2 bytes) if present
        if (flags & 0x0008) and len(data) >= offset + 2:
            accumulated_energy = struct.unpack("<H", data[offset : offset + 2])[0]
            result["accumulated_energy"] = accumulated_energy  # kJ
            offset += 2

        # Parse optional wheel revolution data (6 bytes total) if present
        if (flags & 0x0010) and len(data) >= offset + 6:
            wheel_revolutions = struct.unpack("<I", data[offset : offset + 4])[0]
            wheel_event_time_raw = struct.unpack("<H", data[offset + 4 : offset + 6])[0]
            # Wheel event time is in 1/2048 second units
            wheel_event_time = wheel_event_time_raw / 2048.0

            result.update(
                {
                    "cumulative_wheel_revolutions": wheel_revolutions,
                    "last_wheel_event_time": wheel_event_time,
                }
            )
            offset += 6

        # Parse optional crank revolution data (4 bytes total) if present
        if (flags & 0x0020) and len(data) >= offset + 4:
            crank_revolutions = struct.unpack("<H", data[offset : offset + 2])[0]
            crank_event_time_raw = struct.unpack("<H", data[offset + 2 : offset + 4])[0]
            # Crank event time is in 1/1024 second units
            crank_event_time = crank_event_time_raw / 1024.0

            result.update(
                {
                    "cumulative_crank_revolutions": crank_revolutions,
                    "last_crank_event_time": crank_event_time,
                }
            )
            offset += 4

        # For now, convert result dict to dataclass at the end
        # (Full conversion would require updating all the parsing logic)
        return CyclingPowerMeasurementData(
            flags=result["flags"],
            instantaneous_power=result["instantaneous_power"],
            pedal_power_balance=result.get("pedal_power_balance"),
            accumulated_energy=result.get("accumulated_energy"),
            cumulative_wheel_revolutions=result.get("cumulative_wheel_revolutions"),
            last_wheel_event_time=result.get("last_wheel_event_time"),
            cumulative_crank_revolutions=result.get("cumulative_crank_revolutions"),
            last_crank_event_time=result.get("last_crank_event_time"),
        )

    def encode_value(self, data: CyclingPowerMeasurementData) -> bytearray:  # pylint: disable=too-many-locals,too-many-branches,too-many-statements # Complex cycling power measurement with numerous optional fields
        """Encode cycling power measurement value back to bytes.

        Args:
            data: CyclingPowerMeasurementData containing cycling power measurement data

        Returns:
            Encoded bytes representing the power measurement
        """
        if not isinstance(data, CyclingPowerMeasurementData):
            raise TypeError(
                f"Cycling power measurement data must be a CyclingPowerMeasurementData, "
                f"got {type(data).__name__}"
            )

        instantaneous_power = data.instantaneous_power
        pedal_power_balance = data.pedal_power_balance
        accumulated_energy = data.accumulated_energy
        wheel_revolutions = data.cumulative_wheel_revolutions  # Updated field name
        wheel_event_time = data.last_wheel_event_time
        crank_revolutions = data.cumulative_crank_revolutions  # Updated field name
        crank_event_time = data.last_crank_event_time

        # Build flags based on available data
        flags = 0
        if pedal_power_balance is not None:
            flags |= 0x01  # Pedal power balance present
        if accumulated_energy is not None:
            flags |= 0x04  # Accumulated energy present
        if wheel_revolutions is not None and wheel_event_time is not None:
            flags |= 0x10  # Wheel revolution data present
        if crank_revolutions is not None and crank_event_time is not None:
            flags |= 0x20  # Crank revolution data present

        # Validate instantaneous power (sint16 range)
        if not -32768 <= instantaneous_power <= 32767:
            raise ValueError(
                f"Instantaneous power {instantaneous_power} W exceeds sint16 range"
            )

        # Start with flags and instantaneous power
        result = bytearray()
        result.extend(struct.pack("<H", flags))  # Flags (16-bit)
        result.extend(struct.pack("<h", instantaneous_power))  # Power (sint16)

        # Add optional fields based on flags
        if pedal_power_balance is not None:
            balance = int(pedal_power_balance)
            if not 0 <= balance <= 255:
                raise ValueError(f"Pedal power balance {balance} exceeds uint8 range")
            result.append(balance)

        if accumulated_energy is not None:
            energy = int(accumulated_energy)
            if not 0 <= energy <= 0xFFFF:
                raise ValueError(f"Accumulated energy {energy} exceeds uint16 range")
            result.extend(struct.pack("<H", energy))

        if wheel_revolutions is not None and wheel_event_time is not None:
            wheel_rev = int(wheel_revolutions)
            wheel_time = int(wheel_event_time)
            if not 0 <= wheel_rev <= 0xFFFFFFFF:
                raise ValueError(f"Wheel revolutions {wheel_rev} exceeds uint32 range")
            if not 0 <= wheel_time <= 0xFFFF:
                raise ValueError(f"Wheel event time {wheel_time} exceeds uint16 range")
            result.extend(struct.pack("<I", wheel_rev))
            result.extend(struct.pack("<H", wheel_time))

        if crank_revolutions is not None and crank_event_time is not None:
            crank_rev = int(crank_revolutions)
            crank_time = int(crank_event_time)
            if not 0 <= crank_rev <= 0xFFFF:
                raise ValueError(f"Crank revolutions {crank_rev} exceeds uint16 range")
            if not 0 <= crank_time <= 0xFFFF:
                raise ValueError(f"Crank event time {crank_time} exceeds uint16 range")
            result.extend(struct.pack("<H", crank_rev))
            result.extend(struct.pack("<H", crank_time))

        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "W"  # Watts
