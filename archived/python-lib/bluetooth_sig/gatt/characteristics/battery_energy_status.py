"""Battery Energy Status characteristic implementation.

Implements the Battery Energy Status characteristic (0x2BF0) from the Battery
Service.  An 8-bit flags field controls the presence of six optional medfloat16
(IEEE 11073 SFLOAT) fields.

All flag bits use normal logic (1 = present, 0 = absent).

References:
    Bluetooth SIG Battery Service 1.1
    org.bluetooth.characteristic.battery_energy_status (GSS YAML)
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser, IEEE11073Parser


class BatteryEnergyStatusFlags(IntFlag):
    """Battery Energy Status flags as per Bluetooth SIG specification."""

    EXTERNAL_SOURCE_POWER_PRESENT = 0x01
    PRESENT_VOLTAGE_PRESENT = 0x02
    AVAILABLE_ENERGY_PRESENT = 0x04
    AVAILABLE_BATTERY_CAPACITY_PRESENT = 0x08
    CHARGE_RATE_PRESENT = 0x10
    AVAILABLE_ENERGY_LAST_CHARGE_PRESENT = 0x20


class BatteryEnergyStatus(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Battery Energy Status characteristic.

    Attributes:
        flags: Raw 8-bit flags field.
        external_source_power: Power consumed from external source (watts).
            None if absent.
        present_voltage: Terminal voltage of battery (volts). None if absent.
        available_energy: Available energy (kWh). None if absent.
        available_battery_capacity: Capacity at full charge (kWh).
            None if absent.
        charge_rate: Energy flow into battery (watts, negative = discharge).
            None if absent.
        available_energy_at_last_charge: Available energy at last charge (kWh).
            None if absent.

    """

    flags: BatteryEnergyStatusFlags
    external_source_power: float | None = None
    present_voltage: float | None = None
    available_energy: float | None = None
    available_battery_capacity: float | None = None
    charge_rate: float | None = None
    available_energy_at_last_charge: float | None = None


class BatteryEnergyStatusCharacteristic(BaseCharacteristic[BatteryEnergyStatus]):
    """Battery Energy Status characteristic (0x2BF0).

    Reports battery energy information including voltage, energy capacity,
    and charge/discharge rates.

    Flag-bit assignments (from GSS YAML):
        Bit 0: External Source Power Present
        Bit 1: Present Voltage Present
        Bit 2: Available Energy Present
        Bit 3: Available Battery Capacity Present
        Bit 4: Charge Rate Present
        Bit 5: Available Energy at Last Charge Present
        Bits 6-7: Reserved for Future Use

    All value fields are medfloat16 (IEEE 11073 SFLOAT, 2 bytes each).

    """

    expected_type = BatteryEnergyStatus
    min_length: int = 1  # 1 byte flags only (all fields optional)
    allow_variable_length: bool = True

    # Mapping: (flag_bit, attribute_name) in wire order
    _FIELD_MAP: tuple[tuple[BatteryEnergyStatusFlags, str], ...] = (
        (BatteryEnergyStatusFlags.EXTERNAL_SOURCE_POWER_PRESENT, "external_source_power"),
        (BatteryEnergyStatusFlags.PRESENT_VOLTAGE_PRESENT, "present_voltage"),
        (BatteryEnergyStatusFlags.AVAILABLE_ENERGY_PRESENT, "available_energy"),
        (BatteryEnergyStatusFlags.AVAILABLE_BATTERY_CAPACITY_PRESENT, "available_battery_capacity"),
        (BatteryEnergyStatusFlags.CHARGE_RATE_PRESENT, "charge_rate"),
        (BatteryEnergyStatusFlags.AVAILABLE_ENERGY_LAST_CHARGE_PRESENT, "available_energy_at_last_charge"),
    )

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> BatteryEnergyStatus:
        """Parse Battery Energy Status from raw BLE bytes.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context (unused).
            validate: Whether to validate ranges.

        Returns:
            BatteryEnergyStatus with all present fields populated.

        """
        flags = BatteryEnergyStatusFlags(DataParser.parse_int8(data, 0, signed=False))
        offset = 1
        values: dict[str, float | None] = {}

        for flag_bit, attr_name in self._FIELD_MAP:
            if flags & flag_bit:
                values[attr_name] = IEEE11073Parser.parse_sfloat(data, offset)
                offset += 2
            else:
                values[attr_name] = None

        return BatteryEnergyStatus(flags=flags, **values)

    def _encode_value(self, data: BatteryEnergyStatus) -> bytearray:
        """Encode BatteryEnergyStatus back to BLE bytes.

        Args:
            data: BatteryEnergyStatus instance.

        Returns:
            Encoded bytearray matching the BLE wire format.

        """
        flags = BatteryEnergyStatusFlags(0)

        for flag_bit, attr_name in self._FIELD_MAP:
            if getattr(data, attr_name) is not None:
                flags |= flag_bit

        result = DataParser.encode_int8(int(flags), signed=False)

        for _flag_bit, attr_name in self._FIELD_MAP:
            value = getattr(data, attr_name)
            if value is not None:
                result.extend(IEEE11073Parser.encode_sfloat(value))

        return result
