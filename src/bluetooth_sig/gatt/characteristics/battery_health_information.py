"""Battery Health Information characteristic implementation.

Implements the Battery Health Information characteristic (0x2BEB) from the
Battery Service.  An 8-bit flags field controls the presence of optional fields.

All flag bits use normal logic (1 = present, 0 = absent).

Bit 1 gates two fields simultaneously: Min and Max Designed Operating
Temperature.

References:
    Bluetooth SIG Battery Service 1.1
    org.bluetooth.characteristic.battery_health_information (GSS YAML)
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..constants import SINT8_MAX, SINT8_MIN, UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class BatteryHealthInformationFlags(IntFlag):
    """Battery Health Information flags as per Bluetooth SIG specification."""

    CYCLE_COUNT_DESIGNED_LIFETIME_PRESENT = 0x01
    TEMPERATURE_RANGE_PRESENT = 0x02


class BatteryHealthInformation(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Battery Health Information characteristic.

    Attributes:
        flags: Raw 8-bit flags field.
        cycle_count_designed_lifetime: Designed number of charge cycles.
            None if absent.
        min_designed_operating_temperature: Min operating temperature (C).
            127 means ">126", -128 means "<-127". None if absent.
        max_designed_operating_temperature: Max operating temperature (C).
            127 means ">126", -128 means "<-127". None if absent.

    """

    flags: BatteryHealthInformationFlags
    cycle_count_designed_lifetime: int | None = None
    min_designed_operating_temperature: int | None = None
    max_designed_operating_temperature: int | None = None

    def __post_init__(self) -> None:
        """Validate field ranges."""
        if self.cycle_count_designed_lifetime is not None and not 0 <= self.cycle_count_designed_lifetime <= UINT16_MAX:
            raise ValueError(
                f"Cycle count designed lifetime must be 0-{UINT16_MAX}, got {self.cycle_count_designed_lifetime}"
            )
        if (
            self.min_designed_operating_temperature is not None
            and not SINT8_MIN <= self.min_designed_operating_temperature <= SINT8_MAX
        ):
            raise ValueError(
                f"Min temperature must be {SINT8_MIN}-{SINT8_MAX}, got {self.min_designed_operating_temperature}"
            )
        if (
            self.max_designed_operating_temperature is not None
            and not SINT8_MIN <= self.max_designed_operating_temperature <= SINT8_MAX
        ):
            raise ValueError(
                f"Max temperature must be {SINT8_MIN}-{SINT8_MAX}, got {self.max_designed_operating_temperature}"
            )


class BatteryHealthInformationCharacteristic(
    BaseCharacteristic[BatteryHealthInformation],
):
    """Battery Health Information characteristic (0x2BEB).

    Reports designed battery health parameters including designed cycle count
    and designed operating temperature range.

    Flag-bit assignments (from GSS YAML):
        Bit 0: Cycle Count Designed Lifetime Present
        Bit 1: Min and Max Designed Operating Temperature Present
        Bits 2-7: Reserved for Future Use

    Note: Bit 1 gates two fields (min + max temperature) simultaneously.

    """

    expected_type = BatteryHealthInformation
    min_length: int = 1  # 1 byte flags only (all fields optional)
    allow_variable_length: bool = True

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> BatteryHealthInformation:
        """Parse Battery Health Information from raw BLE bytes.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context (unused).
            validate: Whether to validate ranges.

        Returns:
            BatteryHealthInformation with all present fields populated.

        """
        flags = BatteryHealthInformationFlags(DataParser.parse_int8(data, 0, signed=False))
        offset = 1

        # Bit 0 -- Cycle Count Designed Lifetime (uint16)
        cycle_count_designed_lifetime = None
        if flags & BatteryHealthInformationFlags.CYCLE_COUNT_DESIGNED_LIFETIME_PRESENT:
            cycle_count_designed_lifetime = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        # Bit 1 -- Min AND Max Designed Operating Temperature (2 x sint8)
        min_temp = None
        max_temp = None
        if flags & BatteryHealthInformationFlags.TEMPERATURE_RANGE_PRESENT:
            min_temp = DataParser.parse_int8(data, offset, signed=True)
            offset += 1
            max_temp = DataParser.parse_int8(data, offset, signed=True)
            offset += 1

        return BatteryHealthInformation(
            flags=flags,
            cycle_count_designed_lifetime=cycle_count_designed_lifetime,
            min_designed_operating_temperature=min_temp,
            max_designed_operating_temperature=max_temp,
        )

    def _encode_value(self, data: BatteryHealthInformation) -> bytearray:
        """Encode BatteryHealthInformation back to BLE bytes.

        Args:
            data: BatteryHealthInformation instance.

        Returns:
            Encoded bytearray matching the BLE wire format.

        """
        flags = BatteryHealthInformationFlags(0)

        if data.cycle_count_designed_lifetime is not None:
            flags |= BatteryHealthInformationFlags.CYCLE_COUNT_DESIGNED_LIFETIME_PRESENT
        if data.min_designed_operating_temperature is not None or data.max_designed_operating_temperature is not None:
            flags |= BatteryHealthInformationFlags.TEMPERATURE_RANGE_PRESENT

        result = DataParser.encode_int8(int(flags), signed=False)

        if data.cycle_count_designed_lifetime is not None:
            result.extend(DataParser.encode_int16(data.cycle_count_designed_lifetime, signed=False))
        if flags & BatteryHealthInformationFlags.TEMPERATURE_RANGE_PRESENT:
            min_temp = (
                data.min_designed_operating_temperature if data.min_designed_operating_temperature is not None else 0
            )
            max_temp = (
                data.max_designed_operating_temperature if data.max_designed_operating_temperature is not None else 0
            )
            result.extend(DataParser.encode_int8(min_temp, signed=True))
            result.extend(DataParser.encode_int8(max_temp, signed=True))

        return result
