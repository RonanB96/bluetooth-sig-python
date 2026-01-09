"""Cycling Power Measurement characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..constants import SINT16_MAX, SINT16_MIN, UINT8_MAX, UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .cycling_power_feature import CyclingPowerFeatureCharacteristic
from .utils import DataParser


class CyclingPowerMeasurementFlags(IntFlag):
    """Cycling Power Measurement Flags as per Bluetooth SIG specification."""

    PEDAL_POWER_BALANCE_PRESENT = 0x0001
    PEDAL_POWER_BALANCE_REFERENCE = 0x0002  # 0 = Unknown, 1 = Left
    ACCUMULATED_TORQUE_PRESENT = 0x0004
    ACCUMULATED_ENERGY_PRESENT = 0x0008
    WHEEL_REVOLUTION_DATA_PRESENT = 0x0010
    CRANK_REVOLUTION_DATA_PRESENT = 0x0020
    EXTREME_FORCE_MAGNITUDES_PRESENT = 0x0040
    EXTREME_TORQUE_MAGNITUDES_PRESENT = 0x0080
    EXTREME_ANGLES_PRESENT = 0x0100
    TOP_DEAD_SPOT_ANGLE_PRESENT = 0x0200
    BOTTOM_DEAD_SPOT_ANGLE_PRESENT = 0x0400
    ACCUMULATED_ENERGY_RESERVED = 0x0800


class CyclingPowerMeasurementData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Parsed data from Cycling Power Measurement characteristic."""

    flags: CyclingPowerMeasurementFlags
    instantaneous_power: int  # Watts
    pedal_power_balance: float | None = None  # Percentage (0.5% resolution)
    accumulated_energy: int | None = None  # kJ
    cumulative_wheel_revolutions: int | None = None  # Changed to match decode_value
    last_wheel_event_time: float | None = None  # seconds
    cumulative_crank_revolutions: int | None = None  # Changed to match decode_value
    last_crank_event_time: float | None = None  # seconds

    def __post_init__(self) -> None:
        """Validate cycling power measurement data."""
        flags_value = int(self.flags)
        if not 0 <= flags_value <= UINT16_MAX:
            raise ValueError("Flags must be a uint16 value (0-UINT16_MAX)")
        if not 0 <= self.instantaneous_power <= UINT16_MAX:
            raise ValueError("Instantaneous power must be a uint16 value (0-UINT16_MAX)")


class CyclingPowerMeasurementCharacteristic(BaseCharacteristic[CyclingPowerMeasurementData]):
    """Cycling Power Measurement characteristic (0x2A63).

    Used to transmit cycling power measurement data including
    instantaneous power, pedal power balance, accumulated energy, and
    revolution data.
    """

    # Special values
    UNKNOWN_PEDAL_POWER_BALANCE = 0xFF  # Value indicating unknown power balance

    # Time resolution constants
    WHEEL_TIME_RESOLUTION = 2048.0  # 1/2048 second resolution
    CRANK_TIME_RESOLUTION = 1024.0  # 1/1024 second resolution
    PEDAL_POWER_BALANCE_RESOLUTION = 2.0  # 0.5% resolution

    _manual_unit: str = "W"  # Watts unit for power measurement

    _optional_dependencies = [CyclingPowerFeatureCharacteristic]

    min_length: int = 4  # Flags(2) + Instantaneous Power(2)
    allow_variable_length: bool = True  # Many optional fields based on flags

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> CyclingPowerMeasurementData:  # pylint: disable=too-many-locals # Complex parsing with many optional fields
        """Parse cycling power measurement data according to Bluetooth specification.

        Format: Flags(2) + Instantaneous Power(2) + [Pedal Power Balance(1)] +
        [Accumulated Energy(2)] + [Wheel Revolutions(4)] + [Last Wheel Event Time(2)] +
        [Crank Revolutions(2)] + [Last Crank Event Time(2)]

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            CyclingPowerMeasurementData containing parsed power measurement data.

        Raises:
            ValueError: If data format is invalid.

        """
        if len(data) < 4:
            raise ValueError("Cycling Power Measurement data must be at least 4 bytes")

        # Parse flags (16-bit)
        flags = DataParser.parse_int16(data, 0, signed=False)

        # Parse instantaneous power (16-bit signed integer in watts)
        instantaneous_power = DataParser.parse_int16(data, 2, signed=True)

        offset = 4

        # Parse optional fields
        pedal_power_balance = None
        accumulated_energy = None
        cumulative_wheel_revolutions = None
        last_wheel_event_time = None
        cumulative_crank_revolutions = None
        last_crank_event_time = None

        # Parse optional pedal power balance (1 byte) if present
        if (flags & CyclingPowerMeasurementFlags.PEDAL_POWER_BALANCE_PRESENT) and len(data) >= offset + 1:
            pedal_power_balance_raw = data[offset]
            # Value UNKNOWN_PEDAL_POWER_BALANCE indicates unknown, otherwise percentage (0-100)
            if pedal_power_balance_raw != self.UNKNOWN_PEDAL_POWER_BALANCE:
                pedal_power_balance = pedal_power_balance_raw / self.PEDAL_POWER_BALANCE_RESOLUTION  # 0.5% resolution
            offset += 1

        # Parse optional accumulated energy (2 bytes) if present
        if (flags & CyclingPowerMeasurementFlags.ACCUMULATED_ENERGY_PRESENT) and len(data) >= offset + 2:
            accumulated_energy = DataParser.parse_int16(data, offset, signed=False)  # kJ
            offset += 2

        # Parse optional wheel revolution data (6 bytes total) if present
        if (flags & CyclingPowerMeasurementFlags.WHEEL_REVOLUTION_DATA_PRESENT) and len(data) >= offset + 6:
            cumulative_wheel_revolutions = DataParser.parse_int32(data, offset, signed=False)
            wheel_event_time_raw = DataParser.parse_int16(data, offset + 4, signed=False)
            # Wheel event time is in 1/WHEEL_TIME_RESOLUTION second units
            last_wheel_event_time = wheel_event_time_raw / self.WHEEL_TIME_RESOLUTION
            offset += 6

        # Parse optional crank revolution data (4 bytes total) if present
        if (flags & CyclingPowerMeasurementFlags.CRANK_REVOLUTION_DATA_PRESENT) and len(data) >= offset + 4:
            cumulative_crank_revolutions = DataParser.parse_int16(data, offset, signed=False)
            crank_event_time_raw = DataParser.parse_int16(data, offset + 2, signed=False)
            # Crank event time is in 1/CRANK_TIME_RESOLUTION second units
            last_crank_event_time = crank_event_time_raw / self.CRANK_TIME_RESOLUTION
            offset += 4

        # Validate flags against Cycling Power Feature if available
        if ctx is not None:
            feature_data = self.get_context_characteristic(ctx, CyclingPowerFeatureCharacteristic)
            if feature_data is not None:
                # feature_data is the CyclingPowerFeatureData struct

                # Check if reported features are supported
                reported_features = int(flags)

                # Validate that reported features are actually supported
                if (
                    reported_features & CyclingPowerMeasurementFlags.PEDAL_POWER_BALANCE_PRESENT
                ) and not feature_data.pedal_power_balance_supported:
                    raise ValueError("Pedal power balance reported but not supported by Cycling Power Feature")
                if (
                    reported_features & CyclingPowerMeasurementFlags.ACCUMULATED_ENERGY_PRESENT
                ) and not feature_data.accumulated_energy_supported:
                    raise ValueError("Accumulated energy reported but not supported by Cycling Power Feature")
                if (
                    reported_features & CyclingPowerMeasurementFlags.WHEEL_REVOLUTION_DATA_PRESENT
                ) and not feature_data.wheel_revolution_data_supported:
                    raise ValueError("Wheel revolution data reported but not supported by Cycling Power Feature")
                if (
                    reported_features & CyclingPowerMeasurementFlags.CRANK_REVOLUTION_DATA_PRESENT
                ) and not feature_data.crank_revolution_data_supported:
                    raise ValueError("Crank revolution data reported but not supported by Cycling Power Feature")

        # Create struct with all parsed values
        return CyclingPowerMeasurementData(
            flags=CyclingPowerMeasurementFlags(flags),
            instantaneous_power=instantaneous_power,
            pedal_power_balance=pedal_power_balance,
            accumulated_energy=accumulated_energy,
            cumulative_wheel_revolutions=cumulative_wheel_revolutions,
            last_wheel_event_time=last_wheel_event_time,
            cumulative_crank_revolutions=cumulative_crank_revolutions,
            last_crank_event_time=last_crank_event_time,
        )

    def _encode_value(self, data: CyclingPowerMeasurementData) -> bytearray:  # pylint: disable=too-many-locals,too-many-branches,too-many-statements # Complex cycling power measurement with numerous optional fields
        """Encode cycling power measurement value back to bytes.

        Args:
            data: CyclingPowerMeasurementData containing cycling power measurement data

        Returns:
            Encoded bytes representing the power measurement

        """
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
            flags |= CyclingPowerMeasurementFlags.PEDAL_POWER_BALANCE_PRESENT  # Pedal power balance present
        if accumulated_energy is not None:
            flags |= CyclingPowerMeasurementFlags.ACCUMULATED_ENERGY_PRESENT  # Accumulated energy present
        if wheel_revolutions is not None and wheel_event_time is not None:
            flags |= CyclingPowerMeasurementFlags.WHEEL_REVOLUTION_DATA_PRESENT  # Wheel revolution data present
        if crank_revolutions is not None and crank_event_time is not None:
            flags |= CyclingPowerMeasurementFlags.CRANK_REVOLUTION_DATA_PRESENT  # Crank revolution data present

        # Validate instantaneous power (sint16 range)
        if not SINT16_MIN <= instantaneous_power <= SINT16_MAX:
            raise ValueError(f"Instantaneous power {instantaneous_power} W exceeds sint16 range")

        # Start with flags and instantaneous power
        result = bytearray()
        result.extend(DataParser.encode_int16(flags, signed=False))  # Flags (16-bit)
        result.extend(DataParser.encode_int16(instantaneous_power, signed=True))  # Power (sint16)

        # Add optional fields based on flags
        if pedal_power_balance is not None:
            balance = int(pedal_power_balance * self.PEDAL_POWER_BALANCE_RESOLUTION)  # Convert back to raw value
            if not 0 <= balance <= UINT8_MAX:
                raise ValueError(f"Pedal power balance {balance} exceeds uint8 range")
            result.append(balance)

        if accumulated_energy is not None:
            energy = int(accumulated_energy)
            if not 0 <= energy <= 0xFFFF:
                raise ValueError(f"Accumulated energy {energy} exceeds uint16 range")
            result.extend(DataParser.encode_int16(energy, signed=False))

        if wheel_revolutions is not None and wheel_event_time is not None:
            wheel_rev = int(wheel_revolutions)
            wheel_time = round(wheel_event_time * self.WHEEL_TIME_RESOLUTION)
            if not 0 <= wheel_rev <= 0xFFFFFFFF:
                raise ValueError(f"Wheel revolutions {wheel_rev} exceeds uint32 range")
            if not 0 <= wheel_time <= 0xFFFF:
                raise ValueError(f"Wheel event time {wheel_time} exceeds uint16 range")
            result.extend(DataParser.encode_int32(wheel_rev, signed=False))
            result.extend(DataParser.encode_int16(wheel_time, signed=False))

        if crank_revolutions is not None and crank_event_time is not None:
            crank_rev = int(crank_revolutions)
            crank_time = round(crank_event_time * self.CRANK_TIME_RESOLUTION)
            if not 0 <= crank_rev <= 0xFFFF:
                raise ValueError(f"Crank revolutions {crank_rev} exceeds uint16 range")
            if not 0 <= crank_time <= 0xFFFF:
                raise ValueError(f"Crank event time {crank_time} exceeds uint16 range")
            result.extend(DataParser.encode_int16(crank_rev, signed=False))
            result.extend(DataParser.encode_int16(crank_time, signed=False))

        return result
