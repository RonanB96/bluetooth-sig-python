"""Battery Level Status characteristic implementation."""

from __future__ import annotations

from enum import IntEnum
from typing import Any

import msgspec

from ..constants import UINT8_MAX
from .base import BaseCharacteristic
from .utils import BitFieldUtils


# Bit position constants for Battery Power State characteristic
class BatteryPowerStateBits:  # pylint: disable=too-few-public-methods
    """Bit positions used in Battery Power State characteristic parsing."""

    # Flags byte bit positions
    IDENTIFIER_PRESENT_BIT = 0
    BATTERY_LEVEL_PRESENT_BIT = 1
    ADDITIONAL_INFO_PRESENT_BIT = 2

    # Basic state byte bit positions
    BATTERY_PRESENT_START_BIT = 0
    BATTERY_PRESENT_NUM_BITS = 2
    WIRED_POWER_CONNECTED_BIT = 2
    WIRELESS_POWER_CONNECTED_BIT = 3
    CHARGE_STATE_START_BIT = 4
    CHARGE_STATE_NUM_BITS = 2
    CHARGE_LEVEL_START_BIT = 6
    CHARGE_LEVEL_NUM_BITS = 2

    # Extended state (16-bit) bit positions
    BATTERY_PRESENT_EXT_BIT = 0
    WIRED_POWER_EXT_START_BIT = 1
    WIRED_POWER_EXT_NUM_BITS = 2
    WIRELESS_POWER_EXT_START_BIT = 3
    WIRELESS_POWER_EXT_NUM_BITS = 2
    CHARGE_STATE_EXT_START_BIT = 5
    CHARGE_STATE_EXT_NUM_BITS = 2
    CHARGE_LEVEL_EXT_START_BIT = 7
    CHARGE_LEVEL_EXT_NUM_BITS = 2
    CHARGING_TYPE_START_BIT = 9
    CHARGING_TYPE_NUM_BITS = 3
    FAULT_BITS_START_BIT = 12
    FAULT_BITS_NUM_BITS = 3

    # Fault sub-bits within fault field
    BATTERY_FAULT_BIT = 0
    EXTERNAL_POWER_FAULT_BIT = 1
    OTHER_FAULT_BIT = 2

    # Second byte parsing (charging type + faults)
    CHARGING_TYPE_BYTE_START_BIT = 0
    CHARGING_TYPE_BYTE_NUM_BITS = 3
    FAULT_BYTE_START_BIT = 3
    FAULT_BYTE_NUM_BITS = 5


class BatteryPresentState(IntEnum):
    """Battery present state enumeration."""

    UNKNOWN = 0
    NOT_PRESENT = 1
    PRESENT = 2
    RESERVED = 3

    def __str__(self) -> str:
        return {0: "unknown", 1: "not_present", 2: "present", 3: "reserved"}[self.value]

    @classmethod
    def from_byte(cls, byte_val: int) -> BatteryPresentState:
        """Create enum from byte value with fallback."""
        try:
            return cls(byte_val)
        except ValueError:
            return cls.UNKNOWN


class BatteryChargeState(IntEnum):
    """Battery charge state enumeration."""

    UNKNOWN = 0
    CHARGING = 1
    DISCHARGING = 2
    NOT_CHARGING = 3

    def __str__(self) -> str:
        return {0: "unknown", 1: "charging", 2: "discharging", 3: "not_charging"}[self.value]

    @classmethod
    def from_byte(cls, byte_val: int) -> BatteryChargeState:
        """Create enum from byte value with fallback."""
        try:
            return cls(byte_val)
        except ValueError:
            return cls.UNKNOWN


class BatteryChargeLevel(IntEnum):
    """Battery charge level enumeration."""

    UNKNOWN = 0
    GOOD = 1
    LOW = 2
    CRITICALLY_LOW = 3

    def __str__(self) -> str:
        return {0: "unknown", 1: "good", 2: "low", 3: "critically_low"}[self.value]

    @classmethod
    def from_byte(cls, byte_val: int) -> BatteryChargeLevel:
        """Create enum from byte value with fallback."""
        try:
            return cls(byte_val)
        except ValueError:
            return cls.UNKNOWN


class BatteryChargingType(IntEnum):
    """Battery charging type enumeration."""

    UNKNOWN = 0
    CONSTANT_CURRENT = 1
    CONSTANT_VOLTAGE = 2
    TRICKLE = 3
    FLOAT = 4
    CONSTANT_POWER = 5

    def __str__(self) -> str:
        return {
            0: "unknown",
            1: "constant_current",
            2: "constant_voltage",
            3: "trickle",
            4: "float",
            5: "constant_power",
        }[self.value]

    @classmethod
    def from_byte(cls, byte_val: int) -> BatteryChargingType:
        """Create enum from byte value with fallback."""
        try:
            return cls(byte_val)
        except ValueError:
            return cls.UNKNOWN


class BatteryPowerStateData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Parsed data from Battery Power State characteristic."""

    raw_value: int
    battery_present: BatteryPresentState
    wired_external_power_connected: bool
    wireless_external_power_connected: bool
    battery_charge_state: BatteryChargeState
    battery_charge_level: BatteryChargeLevel
    battery_charging_type: BatteryChargingType
    charging_fault_reason: str | tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        """Validate battery power state data."""
        if not 0 <= self.raw_value <= UINT8_MAX:
            raise ValueError(f"Raw value must be 0-UINT8_MAX, got {self.raw_value}")


class BatteryPowerState(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed battery power state components."""

    battery_present: BatteryPresentState
    wired_external_power_connected: bool
    wireless_external_power_connected: bool
    battery_charge_state: BatteryChargeState
    battery_charge_level: BatteryChargeLevel
    battery_charging_type: BatteryChargingType = BatteryChargingType.UNKNOWN
    charging_fault_reason: str | tuple[str, ...] | None = None


class BatteryPowerStateCharacteristic(BaseCharacteristic):
    """Battery Level Status characteristic (0x2BED).

    This characteristic encodes battery presence, external power
    sources, charging state, charge level and optional extended charging
    information.
    """

    _characteristic_name: str | None = "Battery Level Status"

    # YAML describes this as boolean[] which maps to 'string' in the registry;
    # decode_value returns a dict, but tests and registry expect the declared
    # value_type to be 'string'. Override to keep metadata consistent.
    _manual_value_type = "string"

    def decode_value(self, data: bytearray, _ctx: Any | None = None) -> BatteryPowerStateData:
        """Parse the Battery Level Status value.

        The characteristic supports a 1-byte basic format and a 2-byte
        extended format with charging type and fault codes in the second
        byte. If `data` is empty or None a ValueError is raised.
        """
        if not data or len(data) < 1:
            raise ValueError("Battery Level Status must be at least 1 byte")

        # Single-byte basic state available in all variants
        state_raw = int(data[0])

        # Full SIG format: Flags (1 byte) + Power State (2 bytes little-endian)
        if len(data) >= 3:
            flags = int(data[0])
            power_state_raw = int.from_bytes(data[1:3], byteorder="little", signed=False)

            parsed = self._parse_power_state_16(power_state_raw)

            # validate/advance optional fields indicated in Flags
            offset = 3
            # Identifier needs an explicit, specific error message in tests
            if BitFieldUtils.test_bit(flags, BatteryPowerStateBits.IDENTIFIER_PRESENT_BIT):
                if len(data) < offset + 2:
                    raise ValueError("Identifier indicated by Flags but missing from payload")
                offset += 2

            # Combine remaining optional field checks into one branch to keep
            # static analysis branch count down.
            remaining_needed = offset
            if BitFieldUtils.test_bit(flags, BatteryPowerStateBits.BATTERY_LEVEL_PRESENT_BIT):
                remaining_needed += 1
            if BitFieldUtils.test_bit(flags, BatteryPowerStateBits.ADDITIONAL_INFO_PRESENT_BIT):
                remaining_needed += 1
            if len(data) < remaining_needed:
                raise ValueError("Flags indicate additional fields are missing from payload")
            # We don't need to advance offset further here because we only
            # validate presence (values are not returned in canonical output).

            return BatteryPowerStateData(
                raw_value=int(data[0]),
                battery_present=parsed.battery_present,
                wired_external_power_connected=parsed.wired_external_power_connected,
                wireless_external_power_connected=parsed.wireless_external_power_connected,
                battery_charge_state=parsed.battery_charge_state,
                battery_charge_level=parsed.battery_charge_level,
                battery_charging_type=parsed.battery_charging_type,
                charging_fault_reason=parsed.charging_fault_reason,
            )

        # Two-byte variant: first byte holds basic state, second byte encodes
        # charging type (bits 0-2) and fault bitmap (bits 3-7)
        charging_fault_reason: Any = None

        if len(data) >= 2:
            basic = self._parse_basic_state(state_raw)

            second = int(data[1])

            fault_raw = BitFieldUtils.extract_bit_field(
                second,
                BatteryPowerStateBits.FAULT_BYTE_START_BIT,
                BatteryPowerStateBits.FAULT_BYTE_NUM_BITS,
            )
            if fault_raw != 0:
                fault_reasons: list[str] = []
                if BitFieldUtils.test_bit(fault_raw, BatteryPowerStateBits.BATTERY_FAULT_BIT):
                    fault_reasons.append("battery_fault")
                if BitFieldUtils.test_bit(fault_raw, BatteryPowerStateBits.EXTERNAL_POWER_FAULT_BIT):
                    fault_reasons.append("external_power_fault")
                if BitFieldUtils.test_bit(fault_raw, BatteryPowerStateBits.OTHER_FAULT_BIT):
                    fault_reasons.append("other_fault")
                charging_fault_reason = fault_reasons[0] if len(fault_reasons) == 1 else tuple(fault_reasons)

            return BatteryPowerStateData(
                raw_value=state_raw,
                battery_present=basic.battery_present,
                wired_external_power_connected=basic.wired_external_power_connected,
                wireless_external_power_connected=basic.wireless_external_power_connected,
                battery_charge_state=basic.battery_charge_state,
                battery_charge_level=basic.battery_charge_level,
                battery_charging_type=BatteryChargingType.from_byte(
                    BitFieldUtils.extract_bit_field(
                        second,
                        BatteryPowerStateBits.CHARGING_TYPE_BYTE_START_BIT,
                        BatteryPowerStateBits.CHARGING_TYPE_BYTE_NUM_BITS,
                    )
                ),
                charging_fault_reason=charging_fault_reason,
            )

        # Single-byte basic variant
        basic = self._parse_basic_state(state_raw)
        return BatteryPowerStateData(
            raw_value=state_raw,
            battery_present=basic.battery_present,
            wired_external_power_connected=basic.wired_external_power_connected,
            wireless_external_power_connected=basic.wireless_external_power_connected,
            battery_charge_state=basic.battery_charge_state,
            battery_charge_level=basic.battery_charge_level,
            battery_charging_type=BatteryChargingType.UNKNOWN,
            charging_fault_reason=None,
        )

    def encode_value(self, data: BatteryPowerStateData) -> bytearray:
        """Encode BatteryPowerStateData back to bytes.

        Args:
            data: BatteryPowerStateData instance to encode

        Returns:
            Encoded bytes representing the battery power state

        Raises:
            ValueError: If data contains invalid values
        """
        # For simplicity, we'll encode to the basic single-byte format
        # Future enhancement could support the extended formats

        # Map battery_present to bits 0-1
        battery_present_bits = data.battery_present.value

        # Map charge state to bits 4-5
        charge_state_bits = data.battery_charge_state.value

        # Map charge level to bits 6-7 (need to adjust mapping for basic format)
        # The basic format uses different ordering than the enum values
        charge_level_bits = 0  # Default to UNKNOWN
        if data.battery_charge_level == BatteryChargeLevel.CRITICALLY_LOW:
            charge_level_bits = 1
        elif data.battery_charge_level == BatteryChargeLevel.LOW:
            charge_level_bits = 2
        elif data.battery_charge_level == BatteryChargeLevel.GOOD:
            charge_level_bits = 3

        # Encode single byte
        encoded_byte = BitFieldUtils.merge_bit_fields(
            (
                battery_present_bits,
                BatteryPowerStateBits.BATTERY_PRESENT_START_BIT,
                BatteryPowerStateBits.BATTERY_PRESENT_NUM_BITS,
            ),
            (
                1 if data.wired_external_power_connected else 0,
                BatteryPowerStateBits.WIRED_POWER_CONNECTED_BIT,
                1,
            ),
            (
                1 if data.wireless_external_power_connected else 0,
                BatteryPowerStateBits.WIRELESS_POWER_CONNECTED_BIT,
                1,
            ),
            (
                charge_state_bits,
                BatteryPowerStateBits.CHARGE_STATE_START_BIT,
                BatteryPowerStateBits.CHARGE_STATE_NUM_BITS,
            ),
            (
                charge_level_bits,
                BatteryPowerStateBits.CHARGE_LEVEL_START_BIT,
                BatteryPowerStateBits.CHARGE_LEVEL_NUM_BITS,
            ),
        )

        return bytearray([encoded_byte])

    def _parse_power_state_16(self, power_state_raw: int) -> BatteryPowerState:
        """Parse the 16-bit Power State bitfield into its components.

        Returns a BatteryPowerState dataclass with the parsed
        components.
        """
        # battery present (bit 0): 0 = No/Not present, 1 = Present
        battery_present = (
            BatteryPresentState.PRESENT
            if BitFieldUtils.test_bit(power_state_raw, BatteryPowerStateBits.BATTERY_PRESENT_EXT_BIT)
            else BatteryPresentState.NOT_PRESENT
        )

        # Wired external power: bits 1-2 (2-bit value: 0=No,1=Yes,2=Unknown,3=RFU)
        wired_external_power_connected = (
            BitFieldUtils.extract_bit_field(
                power_state_raw,
                BatteryPowerStateBits.WIRED_POWER_EXT_START_BIT,
                BatteryPowerStateBits.WIRED_POWER_EXT_NUM_BITS,
            )
            == 1
        )

        # Wireless external power: bits 3-4
        wireless_external_power_connected = (
            BitFieldUtils.extract_bit_field(
                power_state_raw,
                BatteryPowerStateBits.WIRELESS_POWER_EXT_START_BIT,
                BatteryPowerStateBits.WIRELESS_POWER_EXT_NUM_BITS,
            )
            == 1
        )

        # Charge state: bits 5-6
        charge_state_raw = BitFieldUtils.extract_bit_field(
            power_state_raw,
            BatteryPowerStateBits.CHARGE_STATE_EXT_START_BIT,
            BatteryPowerStateBits.CHARGE_STATE_EXT_NUM_BITS,
        )
        battery_charge_state = BatteryChargeState.from_byte(charge_state_raw)

        # Charge level: bits 7-8
        charge_level_raw = BitFieldUtils.extract_bit_field(
            power_state_raw,
            BatteryPowerStateBits.CHARGE_LEVEL_EXT_START_BIT,
            BatteryPowerStateBits.CHARGE_LEVEL_EXT_NUM_BITS,
        )
        battery_charge_level = BatteryChargeLevel.from_byte(charge_level_raw)

        # charging type: bits 9-11
        charging_type_raw = BitFieldUtils.extract_bit_field(
            power_state_raw,
            BatteryPowerStateBits.CHARGING_TYPE_START_BIT,
            BatteryPowerStateBits.CHARGING_TYPE_NUM_BITS,
        )
        battery_charging_type = BatteryChargingType.from_byte(charging_type_raw)

        # charging faults are a 3-bit flag field at bits 12..14
        fault_bits = BitFieldUtils.extract_bit_field(
            power_state_raw,
            BatteryPowerStateBits.FAULT_BITS_START_BIT,
            BatteryPowerStateBits.FAULT_BITS_NUM_BITS,
        )
        fault_reasons: list[str] = []
        if BitFieldUtils.test_bit(fault_bits, BatteryPowerStateBits.BATTERY_FAULT_BIT):
            fault_reasons.append("battery_fault")
        if BitFieldUtils.test_bit(fault_bits, BatteryPowerStateBits.EXTERNAL_POWER_FAULT_BIT):
            fault_reasons.append("external_power_fault")
        if BitFieldUtils.test_bit(fault_bits, BatteryPowerStateBits.OTHER_FAULT_BIT):
            fault_reasons.append("other_fault")

        charging_fault_reason = fault_reasons[0] if len(fault_reasons) == 1 else (tuple(fault_reasons) or None)

        return BatteryPowerState(
            battery_present=battery_present,
            wired_external_power_connected=wired_external_power_connected,
            wireless_external_power_connected=wireless_external_power_connected,
            battery_charge_state=battery_charge_state,
            battery_charge_level=battery_charge_level,
            battery_charging_type=battery_charging_type,
            charging_fault_reason=charging_fault_reason,
        )

    def _parse_basic_state(self, state_raw: int) -> BatteryPowerState:
        """Parse the single-byte basic state representation."""
        battery_present_raw = BitFieldUtils.extract_bit_field(
            state_raw,
            BatteryPowerStateBits.BATTERY_PRESENT_START_BIT,
            BatteryPowerStateBits.BATTERY_PRESENT_NUM_BITS,
        )
        battery_present = BatteryPresentState.from_byte(battery_present_raw)

        wired_external_power_connected = bool(
            BitFieldUtils.test_bit(state_raw, BatteryPowerStateBits.WIRED_POWER_CONNECTED_BIT)
        )
        wireless_external_power_connected = bool(
            BitFieldUtils.test_bit(state_raw, BatteryPowerStateBits.WIRELESS_POWER_CONNECTED_BIT)
        )

        charge_state_raw = BitFieldUtils.extract_bit_field(
            state_raw,
            BatteryPowerStateBits.CHARGE_STATE_START_BIT,
            BatteryPowerStateBits.CHARGE_STATE_NUM_BITS,
        )
        battery_charge_state = BatteryChargeState.from_byte(charge_state_raw)

        charge_level_raw = BitFieldUtils.extract_bit_field(
            state_raw,
            BatteryPowerStateBits.CHARGE_LEVEL_START_BIT,
            BatteryPowerStateBits.CHARGE_LEVEL_NUM_BITS,
        )
        # For basic format, the charge level mapping is different
        if charge_level_raw == 0:
            battery_charge_level = BatteryChargeLevel.UNKNOWN
        elif charge_level_raw == 1:
            battery_charge_level = BatteryChargeLevel.CRITICALLY_LOW
        elif charge_level_raw == 2:
            battery_charge_level = BatteryChargeLevel.LOW
        elif charge_level_raw == 3:
            battery_charge_level = BatteryChargeLevel.GOOD
        else:
            battery_charge_level = BatteryChargeLevel.UNKNOWN

        return BatteryPowerState(
            battery_present=battery_present,
            wired_external_power_connected=wired_external_power_connected,
            wireless_external_power_connected=wireless_external_power_connected,
            battery_charge_state=battery_charge_state,
            battery_charge_level=battery_charge_level,
        )
