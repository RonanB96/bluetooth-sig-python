"""Battery Health Status characteristic implementation.

Implements the Battery Health Status characteristic (0x2BEA) from the Battery
Service.  An 8-bit flags field controls the presence of four optional fields.

All flag bits use normal logic (1 = present, 0 = absent).

References:
    Bluetooth SIG Battery Service 1.1
    org.bluetooth.characteristic.battery_health_status (GSS YAML)
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..constants import SINT8_MAX, SINT8_MIN, UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

# Maximum health summary percentage
_HEALTH_SUMMARY_MAX: int = 100

# Temperature sentinels (sint8)
_TEMP_GREATER_THAN_126: int = 0x7F  # raw == 127 means ">126"
_TEMP_LESS_THAN_MINUS_127: int = -128  # raw == -128 (0x80) means "<-127"


class BatteryHealthStatusFlags(IntFlag):
    """Battery Health Status flags as per Bluetooth SIG specification."""

    HEALTH_SUMMARY_PRESENT = 0x01
    CYCLE_COUNT_PRESENT = 0x02
    CURRENT_TEMPERATURE_PRESENT = 0x04
    DEEP_DISCHARGE_COUNT_PRESENT = 0x08


class BatteryHealthStatus(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Battery Health Status characteristic.

    Attributes:
        flags: Raw 8-bit flags field.
        battery_health_summary: Percentage 0-100 representing overall health.
            None if absent.
        cycle_count: Number of charge cycles. None if absent.
        current_temperature: Current temperature in degrees Celsius.
            127 means ">126", -128 means "<-127". None if absent.
        deep_discharge_count: Number of complete discharges. None if absent.

    """

    flags: BatteryHealthStatusFlags
    battery_health_summary: int | None = None
    cycle_count: int | None = None
    current_temperature: int | None = None
    deep_discharge_count: int | None = None

    def __post_init__(self) -> None:
        """Validate field ranges."""
        if self.battery_health_summary is not None and not 0 <= self.battery_health_summary <= _HEALTH_SUMMARY_MAX:
            raise ValueError(
                f"Battery health summary must be 0-{_HEALTH_SUMMARY_MAX}, got {self.battery_health_summary}"
            )
        if self.cycle_count is not None and not 0 <= self.cycle_count <= UINT16_MAX:
            raise ValueError(f"Cycle count must be 0-{UINT16_MAX}, got {self.cycle_count}")
        if self.current_temperature is not None and not SINT8_MIN <= self.current_temperature <= SINT8_MAX:
            raise ValueError(f"Temperature must be {SINT8_MIN}-{SINT8_MAX}, got {self.current_temperature}")
        if self.deep_discharge_count is not None and not 0 <= self.deep_discharge_count <= UINT16_MAX:
            raise ValueError(f"Deep discharge count must be 0-{UINT16_MAX}, got {self.deep_discharge_count}")


class BatteryHealthStatusCharacteristic(BaseCharacteristic[BatteryHealthStatus]):
    """Battery Health Status characteristic (0x2BEA).

    Reports battery health information including summary percentage, cycle
    count, temperature, and deep discharge count.

    Flag-bit assignments (from GSS YAML):
        Bit 0: Battery Health Summary Present
        Bit 1: Cycle Count Present
        Bit 2: Current Temperature Present
        Bit 3: Deep Discharge Count Present
        Bits 4-7: Reserved for Future Use

    """

    expected_type = BatteryHealthStatus
    min_length: int = 1  # 1 byte flags only (all fields optional)
    allow_variable_length: bool = True

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> BatteryHealthStatus:
        """Parse Battery Health Status from raw BLE bytes.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context (unused).
            validate: Whether to validate ranges.

        Returns:
            BatteryHealthStatus with all present fields populated.

        """
        flags = BatteryHealthStatusFlags(DataParser.parse_int8(data, 0, signed=False))
        offset = 1

        # Bit 0 -- Battery Health Summary (uint8, percentage)
        battery_health_summary = None
        if flags & BatteryHealthStatusFlags.HEALTH_SUMMARY_PRESENT:
            battery_health_summary = DataParser.parse_int8(data, offset, signed=False)
            offset += 1

        # Bit 1 -- Cycle Count (uint16)
        cycle_count = None
        if flags & BatteryHealthStatusFlags.CYCLE_COUNT_PRESENT:
            cycle_count = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        # Bit 2 -- Current Temperature (sint8)
        current_temperature = None
        if flags & BatteryHealthStatusFlags.CURRENT_TEMPERATURE_PRESENT:
            current_temperature = DataParser.parse_int8(data, offset, signed=True)
            offset += 1

        # Bit 3 -- Deep Discharge Count (uint16)
        deep_discharge_count = None
        if flags & BatteryHealthStatusFlags.DEEP_DISCHARGE_COUNT_PRESENT:
            deep_discharge_count = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        return BatteryHealthStatus(
            flags=flags,
            battery_health_summary=battery_health_summary,
            cycle_count=cycle_count,
            current_temperature=current_temperature,
            deep_discharge_count=deep_discharge_count,
        )

    def _encode_value(self, data: BatteryHealthStatus) -> bytearray:
        """Encode BatteryHealthStatus back to BLE bytes.

        Args:
            data: BatteryHealthStatus instance.

        Returns:
            Encoded bytearray matching the BLE wire format.

        """
        flags = BatteryHealthStatusFlags(0)

        if data.battery_health_summary is not None:
            flags |= BatteryHealthStatusFlags.HEALTH_SUMMARY_PRESENT
        if data.cycle_count is not None:
            flags |= BatteryHealthStatusFlags.CYCLE_COUNT_PRESENT
        if data.current_temperature is not None:
            flags |= BatteryHealthStatusFlags.CURRENT_TEMPERATURE_PRESENT
        if data.deep_discharge_count is not None:
            flags |= BatteryHealthStatusFlags.DEEP_DISCHARGE_COUNT_PRESENT

        result = DataParser.encode_int8(int(flags), signed=False)

        if data.battery_health_summary is not None:
            result.extend(DataParser.encode_int8(data.battery_health_summary, signed=False))
        if data.cycle_count is not None:
            result.extend(DataParser.encode_int16(data.cycle_count, signed=False))
        if data.current_temperature is not None:
            result.extend(DataParser.encode_int8(data.current_temperature, signed=True))
        if data.deep_discharge_count is not None:
            result.extend(DataParser.encode_int16(data.deep_discharge_count, signed=False))

        return result
