"""Battery Level Status characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from bluetooth_sig.types.battery import (
    BatteryChargeLevel,
    BatteryChargeState,
    BatteryChargingType,
    PowerConnectionState,
    ServiceRequiredState,
)

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils.bit_field_utils import BitFieldUtils
from .utils.data_parser import DataParser


class BatteryLevelStatusFlags(IntFlag):
    """Battery Level Status flags."""

    IDENTIFIER_PRESENT = 1 << 0
    BATTERY_LEVEL_PRESENT = 1 << 1
    ADDITIONAL_STATUS_PRESENT = 1 << 2


class BatteryLevelStatus(msgspec.Struct):
    """Battery Level Status data structure."""

    # Flags as IntFlag
    flags: BatteryLevelStatusFlags

    # Power State
    battery_present: bool
    wired_external_power_connected: PowerConnectionState
    wireless_external_power_connected: PowerConnectionState
    battery_charge_state: BatteryChargeState
    battery_charge_level: BatteryChargeLevel
    charging_type: BatteryChargingType
    charging_fault_battery: bool
    charging_fault_external_power: bool
    charging_fault_other: bool

    # Optional fields
    identifier: int | None = None  # uint16
    battery_level: int | None = None  # uint8
    service_required: ServiceRequiredState | None = None
    battery_fault: bool | None = None


class BatteryLevelStatusCharacteristic(BaseCharacteristic):
    """Battery Level Status characteristic (0x2BED).

    org.bluetooth.characteristic.battery_level_status
    """

    # Bit field constants for power state
    BIT_START_BATTERY_PRESENT = 0
    BIT_WIDTH_BATTERY_PRESENT = 1
    BIT_START_WIRED_POWER = 1
    BIT_WIDTH_WIRED_POWER = 2
    BIT_START_WIRELESS_POWER = 3
    BIT_WIDTH_WIRELESS_POWER = 2
    BIT_START_CHARGE_STATE = 5
    BIT_WIDTH_CHARGE_STATE = 2
    BIT_START_CHARGE_LEVEL = 7
    BIT_WIDTH_CHARGE_LEVEL = 2
    BIT_START_CHARGING_TYPE = 9
    BIT_WIDTH_CHARGING_TYPE = 3
    BIT_START_FAULT_BATTERY = 12
    BIT_WIDTH_FAULT_BATTERY = 1
    BIT_START_FAULT_EXTERNAL = 13
    BIT_WIDTH_FAULT_EXTERNAL = 1
    BIT_START_FAULT_OTHER = 14
    BIT_WIDTH_FAULT_OTHER = 1

    # Bit field constants for additional status
    BIT_START_SERVICE_REQUIRED = 0
    BIT_WIDTH_SERVICE_REQUIRED = 2
    BIT_START_BATTERY_FAULT = 2
    BIT_WIDTH_BATTERY_FAULT = 1

    allow_variable_length = True
    min_length = 3  # flags (1) + power_state (2)
    max_length = 7  # + identifier (2) + battery_level (1) + additional_status (1)

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> BatteryLevelStatus:  # pylint: disable=too-many-locals
        """Decode the battery level status value."""
        offset = 0

        # Parse flags (1 byte)
        flags = BatteryLevelStatusFlags(DataParser.parse_int8(data, offset, signed=False))
        offset += 1

        # Parse power state (2 bytes)
        power_state = DataParser.parse_int16(data, offset, signed=False)
        offset += 2

        battery_present = BitFieldUtils.test_bit(power_state, self.BIT_START_BATTERY_PRESENT)
        wired_external_power_connected = PowerConnectionState(
            BitFieldUtils.extract_bit_field(power_state, self.BIT_START_WIRED_POWER, self.BIT_WIDTH_WIRED_POWER)
        )
        wireless_external_power_connected = PowerConnectionState(
            BitFieldUtils.extract_bit_field(power_state, self.BIT_START_WIRELESS_POWER, self.BIT_WIDTH_WIRELESS_POWER)
        )
        battery_charge_state = BatteryChargeState(
            BitFieldUtils.extract_bit_field(power_state, self.BIT_START_CHARGE_STATE, self.BIT_WIDTH_CHARGE_STATE)
        )
        battery_charge_level = BatteryChargeLevel(
            BitFieldUtils.extract_bit_field(power_state, self.BIT_START_CHARGE_LEVEL, self.BIT_WIDTH_CHARGE_LEVEL)
        )
        charging_type = BatteryChargingType(
            BitFieldUtils.extract_bit_field(power_state, self.BIT_START_CHARGING_TYPE, self.BIT_WIDTH_CHARGING_TYPE)
        )
        charging_fault_battery = BitFieldUtils.test_bit(power_state, self.BIT_START_FAULT_BATTERY)
        charging_fault_external_power = BitFieldUtils.test_bit(power_state, self.BIT_START_FAULT_EXTERNAL)
        charging_fault_other = BitFieldUtils.test_bit(power_state, self.BIT_START_FAULT_OTHER)

        # Optional identifier
        identifier = None
        if flags & BatteryLevelStatusFlags.IDENTIFIER_PRESENT:
            identifier = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        # Optional battery level
        battery_level = None
        if flags & BatteryLevelStatusFlags.BATTERY_LEVEL_PRESENT:
            battery_level = DataParser.parse_int8(data, offset, signed=False)
            offset += 1

        # Optional additional status
        service_required = None
        battery_fault = None
        if flags & BatteryLevelStatusFlags.ADDITIONAL_STATUS_PRESENT:
            additional_status = DataParser.parse_int8(data, offset, signed=False)
            service_required = ServiceRequiredState(
                BitFieldUtils.extract_bit_field(
                    additional_status, self.BIT_START_SERVICE_REQUIRED, self.BIT_WIDTH_SERVICE_REQUIRED
                )
            )
            battery_fault = BitFieldUtils.test_bit(additional_status, self.BIT_START_BATTERY_FAULT)

        return BatteryLevelStatus(
            flags=flags,
            battery_present=battery_present,
            wired_external_power_connected=wired_external_power_connected,
            wireless_external_power_connected=wireless_external_power_connected,
            battery_charge_state=battery_charge_state,
            battery_charge_level=battery_charge_level,
            charging_type=charging_type,
            charging_fault_battery=charging_fault_battery,
            charging_fault_external_power=charging_fault_external_power,
            charging_fault_other=charging_fault_other,
            identifier=identifier,
            battery_level=battery_level,
            service_required=service_required,
            battery_fault=battery_fault,
        )

    def encode_value(self, data: BatteryLevelStatus) -> bytearray:
        """Encode the battery level status value."""
        result = bytearray()

        # Encode flags
        flags = BatteryLevelStatusFlags(0)
        if data.identifier is not None:
            flags |= BatteryLevelStatusFlags.IDENTIFIER_PRESENT
        if data.battery_level is not None:
            flags |= BatteryLevelStatusFlags.BATTERY_LEVEL_PRESENT
        if data.service_required is not None or data.battery_fault is not None:
            flags |= BatteryLevelStatusFlags.ADDITIONAL_STATUS_PRESENT
        result.extend(DataParser.encode_int8(flags.value, signed=False))

        # Encode power state
        power_state = 0
        if data.battery_present:
            power_state = BitFieldUtils.set_bit(power_state, self.BIT_START_BATTERY_PRESENT)
        power_state = BitFieldUtils.set_bit_field(
            power_state,
            data.wired_external_power_connected.value,
            self.BIT_START_WIRED_POWER,
            self.BIT_WIDTH_WIRED_POWER,
        )
        power_state = BitFieldUtils.set_bit_field(
            power_state,
            data.wireless_external_power_connected.value,
            self.BIT_START_WIRELESS_POWER,
            self.BIT_WIDTH_WIRELESS_POWER,
        )
        power_state = BitFieldUtils.set_bit_field(
            power_state, data.battery_charge_state.value, self.BIT_START_CHARGE_STATE, self.BIT_WIDTH_CHARGE_STATE
        )
        power_state = BitFieldUtils.set_bit_field(
            power_state, data.battery_charge_level.value, self.BIT_START_CHARGE_LEVEL, self.BIT_WIDTH_CHARGE_LEVEL
        )
        power_state = BitFieldUtils.set_bit_field(
            power_state, data.charging_type.value, self.BIT_START_CHARGING_TYPE, self.BIT_WIDTH_CHARGING_TYPE
        )
        if data.charging_fault_battery:
            power_state = BitFieldUtils.set_bit(power_state, self.BIT_START_FAULT_BATTERY)
        if data.charging_fault_external_power:
            power_state = BitFieldUtils.set_bit(power_state, self.BIT_START_FAULT_EXTERNAL)
        if data.charging_fault_other:
            power_state = BitFieldUtils.set_bit(power_state, self.BIT_START_FAULT_OTHER)
        result.extend(DataParser.encode_int16(power_state, signed=False))

        # Optional identifier
        if data.identifier is not None:
            result.extend(DataParser.encode_int16(data.identifier, signed=False))

        # Optional battery level
        if data.battery_level is not None:
            result.extend(DataParser.encode_int8(data.battery_level, signed=False))

        # Optional additional status
        if data.service_required is not None or data.battery_fault is not None:
            additional_status = 0
            if data.service_required is not None:
                additional_status = BitFieldUtils.set_bit_field(
                    additional_status,
                    data.service_required.value,
                    self.BIT_START_SERVICE_REQUIRED,
                    self.BIT_WIDTH_SERVICE_REQUIRED,
                )
            if data.battery_fault:
                additional_status = BitFieldUtils.set_bit(additional_status, self.BIT_START_BATTERY_FAULT)
            result.extend(DataParser.encode_int8(additional_status, signed=False))

        return result
