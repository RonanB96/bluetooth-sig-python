"""Cycling Power Measurement characteristic implementation."""

from __future__ import annotations

from enum import IntFlag
from typing import Any, ClassVar

import msgspec

from ..constants import SINT16_MAX, SINT16_MIN, UINT8_MAX, UINT16_MAX, UINT32_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .cycling_power_feature import CyclingPowerFeatureCharacteristic
from .utils import DataParser


class CyclingPowerMeasurementFlags(IntFlag):
    """Cycling Power Measurement Flags as per CPS v1.1 Table 3.2."""

    PEDAL_POWER_BALANCE_PRESENT = 0x0001  # bit 0
    PEDAL_POWER_BALANCE_REFERENCE = 0x0002  # bit 1 — 0=Unknown, 1=Left
    ACCUMULATED_TORQUE_PRESENT = 0x0004  # bit 2
    ACCUMULATED_TORQUE_SOURCE = 0x0008  # bit 3 — 0=Wheel Based, 1=Crank Based
    WHEEL_REVOLUTION_DATA_PRESENT = 0x0010  # bit 4
    CRANK_REVOLUTION_DATA_PRESENT = 0x0020  # bit 5
    EXTREME_FORCE_MAGNITUDES_PRESENT = 0x0040  # bit 6
    EXTREME_TORQUE_MAGNITUDES_PRESENT = 0x0080  # bit 7
    EXTREME_ANGLES_PRESENT = 0x0100  # bit 8
    TOP_DEAD_SPOT_ANGLE_PRESENT = 0x0200  # bit 9
    BOTTOM_DEAD_SPOT_ANGLE_PRESENT = 0x0400  # bit 10
    ACCUMULATED_ENERGY_PRESENT = 0x0800  # bit 11
    OFFSET_COMPENSATION_INDICATOR = 0x1000  # bit 12


class CyclingPowerMeasurementData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Parsed data from Cycling Power Measurement characteristic."""

    flags: CyclingPowerMeasurementFlags
    instantaneous_power: int  # Watts (sint16)
    pedal_power_balance: float | None = None  # Percentage (0.5% resolution)
    accumulated_torque: float | None = None  # Newton metres (1/32 Nm resolution)
    accumulated_energy: int | None = None  # kJ
    cumulative_wheel_revolutions: int | None = None
    last_wheel_event_time: float | None = None  # seconds
    cumulative_crank_revolutions: int | None = None
    last_crank_event_time: float | None = None  # seconds
    maximum_force_magnitude: int | None = None  # Newtons (sint16)
    minimum_force_magnitude: int | None = None  # Newtons (sint16)
    maximum_torque_magnitude: float | None = None  # Nm (sint16, 1/32 resolution)
    minimum_torque_magnitude: float | None = None  # Nm (sint16, 1/32 resolution)
    maximum_angle: int | None = None  # degrees (uint16)
    minimum_angle: int | None = None  # degrees (uint16)
    top_dead_spot_angle: int | None = None  # degrees (uint16)
    bottom_dead_spot_angle: int | None = None  # degrees (uint16)

    def __post_init__(self) -> None:
        """Validate cycling power measurement data."""
        flags_value = int(self.flags)
        if not 0 <= flags_value <= UINT16_MAX:
            raise ValueError("Flags must be a uint16 value (0-UINT16_MAX)")
        if not SINT16_MIN <= self.instantaneous_power <= SINT16_MAX:
            raise ValueError("Instantaneous power must be a sint16 value")


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
    ACCUMULATED_TORQUE_RESOLUTION = 32.0  # 1/32 Nm resolution

    _manual_unit: str = "W"  # Watts unit for power measurement

    _optional_dependencies: ClassVar[list[type[BaseCharacteristic[Any]]]] = [CyclingPowerFeatureCharacteristic]

    min_length: int = 4  # Flags(2) + Instantaneous Power(2)
    allow_variable_length: bool = True  # Many optional fields based on flags

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> CyclingPowerMeasurementData:  # pylint: disable=too-many-locals  # Complex parsing with many optional fields
        """Parse cycling power measurement data according to Bluetooth specification.

        Format: Flags(2) + Instantaneous Power(2) + [Pedal Power Balance(1)] +
        [Accumulated Torque(2)] + [Wheel Revolutions(4) + Last Wheel Event Time(2)] +
        [Crank Revolutions(2) + Last Crank Event Time(2)] + [Accumulated Energy(2)]

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).
            validate: Whether to validate ranges (default True)

        Returns:
            CyclingPowerMeasurementData containing parsed power measurement data.

        Raises:
            ValueError: If data format is invalid.

        """
        # Parse flags (16-bit)
        flags = DataParser.parse_int16(data, 0, signed=False)

        # Parse instantaneous power (16-bit signed integer in watts)
        instantaneous_power = DataParser.parse_int16(data, 2, signed=True)

        offset = 4

        # Parse optional fields
        pedal_power_balance = None
        accumulated_torque = None
        accumulated_energy = None
        cumulative_wheel_revolutions = None
        last_wheel_event_time = None
        cumulative_crank_revolutions = None
        last_crank_event_time = None
        maximum_force_magnitude = None
        minimum_force_magnitude = None
        maximum_torque_magnitude = None
        minimum_torque_magnitude = None
        maximum_angle = None
        minimum_angle = None
        top_dead_spot_angle = None
        bottom_dead_spot_angle = None

        # Parse optional pedal power balance (1 byte) if present (bit 0)
        if (flags & CyclingPowerMeasurementFlags.PEDAL_POWER_BALANCE_PRESENT) and len(data) >= offset + 1:
            pedal_power_balance_raw = data[offset]
            # Value UNKNOWN_PEDAL_POWER_BALANCE indicates unknown, otherwise percentage
            if pedal_power_balance_raw != self.UNKNOWN_PEDAL_POWER_BALANCE:
                pedal_power_balance = pedal_power_balance_raw / self.PEDAL_POWER_BALANCE_RESOLUTION  # 0.5% resolution
            offset += 1

        # Parse optional accumulated torque (2 bytes, uint16, 1/32 Nm resolution) if present (bit 2)
        if (flags & CyclingPowerMeasurementFlags.ACCUMULATED_TORQUE_PRESENT) and len(data) >= offset + 2:
            accumulated_torque_raw = DataParser.parse_int16(data, offset, signed=False)
            accumulated_torque = accumulated_torque_raw / self.ACCUMULATED_TORQUE_RESOLUTION
            offset += 2

        # Parse optional wheel revolution data (6 bytes total) if present (bit 4)
        if (flags & CyclingPowerMeasurementFlags.WHEEL_REVOLUTION_DATA_PRESENT) and len(data) >= offset + 6:
            cumulative_wheel_revolutions = DataParser.parse_int32(data, offset, signed=False)
            wheel_event_time_raw = DataParser.parse_int16(data, offset + 4, signed=False)
            # Wheel event time is in 1/WHEEL_TIME_RESOLUTION second units
            last_wheel_event_time = wheel_event_time_raw / self.WHEEL_TIME_RESOLUTION
            offset += 6

        # Parse optional crank revolution data (4 bytes total) if present (bit 5)
        if (flags & CyclingPowerMeasurementFlags.CRANK_REVOLUTION_DATA_PRESENT) and len(data) >= offset + 4:
            cumulative_crank_revolutions = DataParser.parse_int16(data, offset, signed=False)
            crank_event_time_raw = DataParser.parse_int16(data, offset + 2, signed=False)
            # Crank event time is in 1/CRANK_TIME_RESOLUTION second units
            last_crank_event_time = crank_event_time_raw / self.CRANK_TIME_RESOLUTION
            offset += 4

        # Parse optional extreme force magnitudes (4 bytes: max sint16 + min sint16) if present (bit 6)
        if (flags & CyclingPowerMeasurementFlags.EXTREME_FORCE_MAGNITUDES_PRESENT) and len(data) >= offset + 4:
            maximum_force_magnitude = DataParser.parse_int16(data, offset, signed=True)
            minimum_force_magnitude = DataParser.parse_int16(data, offset + 2, signed=True)
            offset += 4

        # Parse optional extreme torque magnitudes (4 bytes: max sint16 + min sint16, 1/32 Nm) if present (bit 7)
        if (flags & CyclingPowerMeasurementFlags.EXTREME_TORQUE_MAGNITUDES_PRESENT) and len(data) >= offset + 4:
            maximum_torque_magnitude = DataParser.parse_int16(data, offset, signed=True) / 32.0
            minimum_torque_magnitude = DataParser.parse_int16(data, offset + 2, signed=True) / 32.0
            offset += 4

        # Parse optional extreme angles (3 bytes packed: max uint12 + min uint12) if present (bit 8)
        if (flags & CyclingPowerMeasurementFlags.EXTREME_ANGLES_PRESENT) and len(data) >= offset + 3:
            raw_bytes = data[offset : offset + 3]
            combined = raw_bytes[0] | (raw_bytes[1] << 8) | (raw_bytes[2] << 16)
            maximum_angle = combined & 0x0FFF
            minimum_angle = (combined >> 12) & 0x0FFF
            offset += 3

        # Parse optional top dead spot angle (2 bytes, uint16 degrees) if present (bit 9)
        if (flags & CyclingPowerMeasurementFlags.TOP_DEAD_SPOT_ANGLE_PRESENT) and len(data) >= offset + 2:
            top_dead_spot_angle = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        # Parse optional bottom dead spot angle (2 bytes, uint16 degrees) if present (bit 10)
        if (flags & CyclingPowerMeasurementFlags.BOTTOM_DEAD_SPOT_ANGLE_PRESENT) and len(data) >= offset + 2:
            bottom_dead_spot_angle = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        # Parse optional accumulated energy (2 bytes, uint16, kJ) if present (bit 11)
        if (flags & CyclingPowerMeasurementFlags.ACCUMULATED_ENERGY_PRESENT) and len(data) >= offset + 2:
            accumulated_energy = DataParser.parse_int16(data, offset, signed=False)  # kJ
            offset += 2

        # Validate flags against Cycling Power Feature if available
        if ctx is not None:
            feature_data = self.get_context_characteristic(ctx, CyclingPowerFeatureCharacteristic)
            if feature_data is not None:
                from .cycling_power_feature import CyclingPowerFeatures  # noqa: PLC0415 — local import to avoid cycle

                # Validate that reported features are actually supported
                if (flags & CyclingPowerMeasurementFlags.PEDAL_POWER_BALANCE_PRESENT) and not (
                    feature_data.features & CyclingPowerFeatures.PEDAL_POWER_BALANCE_SUPPORTED
                ):
                    raise ValueError("Pedal power balance reported but not supported by Cycling Power Feature")
                if (flags & CyclingPowerMeasurementFlags.ACCUMULATED_ENERGY_PRESENT) and not (
                    feature_data.features & CyclingPowerFeatures.ACCUMULATED_ENERGY_SUPPORTED
                ):
                    raise ValueError("Accumulated energy reported but not supported by Cycling Power Feature")
                if (flags & CyclingPowerMeasurementFlags.WHEEL_REVOLUTION_DATA_PRESENT) and not (
                    feature_data.features & CyclingPowerFeatures.WHEEL_REVOLUTION_DATA_SUPPORTED
                ):
                    raise ValueError("Wheel revolution data reported but not supported by Cycling Power Feature")
                if (flags & CyclingPowerMeasurementFlags.CRANK_REVOLUTION_DATA_PRESENT) and not (
                    feature_data.features & CyclingPowerFeatures.CRANK_REVOLUTION_DATA_SUPPORTED
                ):
                    raise ValueError("Crank revolution data reported but not supported by Cycling Power Feature")

        # Create struct with all parsed values
        return CyclingPowerMeasurementData(
            flags=CyclingPowerMeasurementFlags(flags),
            instantaneous_power=instantaneous_power,
            pedal_power_balance=pedal_power_balance,
            accumulated_torque=accumulated_torque,
            accumulated_energy=accumulated_energy,
            cumulative_wheel_revolutions=cumulative_wheel_revolutions,
            last_wheel_event_time=last_wheel_event_time,
            cumulative_crank_revolutions=cumulative_crank_revolutions,
            last_crank_event_time=last_crank_event_time,
            maximum_force_magnitude=maximum_force_magnitude,
            minimum_force_magnitude=minimum_force_magnitude,
            maximum_torque_magnitude=maximum_torque_magnitude,
            minimum_torque_magnitude=minimum_torque_magnitude,
            maximum_angle=maximum_angle,
            minimum_angle=minimum_angle,
            top_dead_spot_angle=top_dead_spot_angle,
            bottom_dead_spot_angle=bottom_dead_spot_angle,
        )

    def _encode_value(self, data: CyclingPowerMeasurementData) -> bytearray:  # noqa: PLR0912  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """Encode cycling power measurement value back to bytes.

        Args:
            data: CyclingPowerMeasurementData containing cycling power measurement data

        Returns:
            Encoded bytes representing the power measurement

        """
        instantaneous_power = data.instantaneous_power
        pedal_power_balance = data.pedal_power_balance
        accumulated_torque = data.accumulated_torque
        accumulated_energy = data.accumulated_energy
        wheel_revolutions = data.cumulative_wheel_revolutions
        wheel_event_time = data.last_wheel_event_time
        crank_revolutions = data.cumulative_crank_revolutions
        crank_event_time = data.last_crank_event_time

        # Build flags based on available data
        flags = 0
        if pedal_power_balance is not None:
            flags |= CyclingPowerMeasurementFlags.PEDAL_POWER_BALANCE_PRESENT
        if accumulated_torque is not None:
            flags |= CyclingPowerMeasurementFlags.ACCUMULATED_TORQUE_PRESENT
        if wheel_revolutions is not None and wheel_event_time is not None:
            flags |= CyclingPowerMeasurementFlags.WHEEL_REVOLUTION_DATA_PRESENT
        if crank_revolutions is not None and crank_event_time is not None:
            flags |= CyclingPowerMeasurementFlags.CRANK_REVOLUTION_DATA_PRESENT
        if data.maximum_force_magnitude is not None and data.minimum_force_magnitude is not None:
            flags |= CyclingPowerMeasurementFlags.EXTREME_FORCE_MAGNITUDES_PRESENT
        if data.maximum_torque_magnitude is not None and data.minimum_torque_magnitude is not None:
            flags |= CyclingPowerMeasurementFlags.EXTREME_TORQUE_MAGNITUDES_PRESENT
        if data.maximum_angle is not None and data.minimum_angle is not None:
            flags |= CyclingPowerMeasurementFlags.EXTREME_ANGLES_PRESENT
        if data.top_dead_spot_angle is not None:
            flags |= CyclingPowerMeasurementFlags.TOP_DEAD_SPOT_ANGLE_PRESENT
        if data.bottom_dead_spot_angle is not None:
            flags |= CyclingPowerMeasurementFlags.BOTTOM_DEAD_SPOT_ANGLE_PRESENT
        if accumulated_energy is not None:
            flags |= CyclingPowerMeasurementFlags.ACCUMULATED_ENERGY_PRESENT

        # Validate instantaneous power (sint16 range)
        if not SINT16_MIN <= instantaneous_power <= SINT16_MAX:
            raise ValueError(f"Instantaneous power {instantaneous_power} W exceeds sint16 range")

        # Start with flags and instantaneous power
        result = bytearray()
        result.extend(DataParser.encode_int16(flags, signed=False))  # Flags (16-bit)
        result.extend(DataParser.encode_int16(instantaneous_power, signed=True))  # Power (sint16)

        # Add optional fields in spec order (per CPS v1.1 §3.2.1)
        if pedal_power_balance is not None:
            balance = int(pedal_power_balance * self.PEDAL_POWER_BALANCE_RESOLUTION)
            if not 0 <= balance <= UINT8_MAX:
                raise ValueError(f"Pedal power balance {balance} exceeds uint8 range")
            result.append(balance)

        if accumulated_torque is not None:
            torque_raw = round(accumulated_torque * self.ACCUMULATED_TORQUE_RESOLUTION)
            if not 0 <= torque_raw <= UINT16_MAX:
                raise ValueError(f"Accumulated torque {torque_raw} exceeds uint16 range")
            result.extend(DataParser.encode_int16(torque_raw, signed=False))

        if wheel_revolutions is not None and wheel_event_time is not None:
            wheel_rev = int(wheel_revolutions)
            wheel_time = round(wheel_event_time * self.WHEEL_TIME_RESOLUTION)
            if not 0 <= wheel_rev <= UINT32_MAX:
                raise ValueError(f"Wheel revolutions {wheel_rev} exceeds uint32 range")
            if not 0 <= wheel_time <= UINT16_MAX:
                raise ValueError(f"Wheel event time {wheel_time} exceeds uint16 range")
            result.extend(DataParser.encode_int32(wheel_rev, signed=False))
            result.extend(DataParser.encode_int16(wheel_time, signed=False))

        if crank_revolutions is not None and crank_event_time is not None:
            crank_rev = int(crank_revolutions)
            crank_time = round(crank_event_time * self.CRANK_TIME_RESOLUTION)
            if not 0 <= crank_rev <= UINT16_MAX:
                raise ValueError(f"Crank revolutions {crank_rev} exceeds uint16 range")
            if not 0 <= crank_time <= UINT16_MAX:
                raise ValueError(f"Crank event time {crank_time} exceeds uint16 range")
            result.extend(DataParser.encode_int16(crank_rev, signed=False))
            result.extend(DataParser.encode_int16(crank_time, signed=False))

        # Encode extreme force magnitudes (bit 6): max sint16 + min sint16
        if data.maximum_force_magnitude is not None and data.minimum_force_magnitude is not None:
            if not SINT16_MIN <= data.maximum_force_magnitude <= SINT16_MAX:
                raise ValueError(f"Maximum force magnitude {data.maximum_force_magnitude} exceeds sint16 range")
            if not SINT16_MIN <= data.minimum_force_magnitude <= SINT16_MAX:
                raise ValueError(f"Minimum force magnitude {data.minimum_force_magnitude} exceeds sint16 range")
            result.extend(DataParser.encode_int16(data.maximum_force_magnitude, signed=True))
            result.extend(DataParser.encode_int16(data.minimum_force_magnitude, signed=True))

        # Encode extreme torque magnitudes (bit 7): max sint16 + min sint16, 1/32 Nm resolution
        if data.maximum_torque_magnitude is not None and data.minimum_torque_magnitude is not None:
            max_torque_raw = round(data.maximum_torque_magnitude * 32)
            min_torque_raw = round(data.minimum_torque_magnitude * 32)
            if not SINT16_MIN <= max_torque_raw <= SINT16_MAX:
                raise ValueError(f"Maximum torque magnitude raw {max_torque_raw} exceeds sint16 range")
            if not SINT16_MIN <= min_torque_raw <= SINT16_MAX:
                raise ValueError(f"Minimum torque magnitude raw {min_torque_raw} exceeds sint16 range")
            result.extend(DataParser.encode_int16(max_torque_raw, signed=True))
            result.extend(DataParser.encode_int16(min_torque_raw, signed=True))

        # Encode extreme angles (bit 8): two uint12 packed in 3 bytes
        if data.maximum_angle is not None and data.minimum_angle is not None:
            max_ang = data.maximum_angle & 0x0FFF
            min_ang = data.minimum_angle & 0x0FFF
            combined = max_ang | (min_ang << 12)
            result.append(combined & 0xFF)
            result.append((combined >> 8) & 0xFF)
            result.append((combined >> 16) & 0xFF)

        # Encode top dead spot angle (bit 9): uint16 degrees
        if data.top_dead_spot_angle is not None:
            if not 0 <= data.top_dead_spot_angle <= UINT16_MAX:
                raise ValueError(f"Top dead spot angle {data.top_dead_spot_angle} exceeds uint16 range")
            result.extend(DataParser.encode_int16(data.top_dead_spot_angle, signed=False))

        # Encode bottom dead spot angle (bit 10): uint16 degrees
        if data.bottom_dead_spot_angle is not None:
            if not 0 <= data.bottom_dead_spot_angle <= UINT16_MAX:
                raise ValueError(f"Bottom dead spot angle {data.bottom_dead_spot_angle} exceeds uint16 range")
            result.extend(DataParser.encode_int16(data.bottom_dead_spot_angle, signed=False))

        if accumulated_energy is not None:
            energy = int(accumulated_energy)
            if not 0 <= energy <= UINT16_MAX:
                raise ValueError(f"Accumulated energy {energy} exceeds uint16 range")
            result.extend(DataParser.encode_int16(energy, signed=False))

        return result
