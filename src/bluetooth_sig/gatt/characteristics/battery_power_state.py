"""Battery Level Status characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any

from .base import BaseCharacteristic


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
        return {0: "unknown", 1: "charging", 2: "discharging", 3: "not_charging"}[
            self.value
        ]

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


@dataclass
class BatteryPowerStateData:  # pylint: disable=too-many-instance-attributes
    """Parsed data from Battery Power State characteristic."""

    raw_value: int
    battery_present: BatteryPresentState
    wired_external_power_connected: bool
    wireless_external_power_connected: bool
    battery_charge_state: BatteryChargeState
    battery_charge_level: BatteryChargeLevel
    battery_charging_type: BatteryChargingType
    charging_fault_reason: str | list[str] | None = None

    def __post_init__(self) -> None:
        """Validate battery power state data."""
        if not 0 <= self.raw_value <= 255:
            raise ValueError(f"Raw value must be 0-255, got {self.raw_value}")


@dataclass
class BatteryPowerStateCharacteristic(BaseCharacteristic):
    """Battery Level Status characteristic (0x2BED).

    This characteristic encodes battery presence, external power sources,
    charging state, charge level and optional extended charging information.
    """

    _characteristic_name: str = "Battery Level Status"
    # YAML describes this as boolean[] which maps to 'string' in the registry;
    # decode_value returns a dict, but tests and registry expect the declared
    # value_type to be 'string'. Override to keep metadata consistent.
    _manual_value_type: str = "string"

    def decode_value(self, data: bytearray) -> BatteryPowerStateData:
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
            power_state_raw = int.from_bytes(
                data[1:3], byteorder="little", signed=False
            )

            parsed = self._parse_power_state_16(power_state_raw)

            # validate/advance optional fields indicated in Flags
            offset = 3
            # Identifier needs an explicit, specific error message in tests
            if flags & 0x01:
                if len(data) < offset + 2:
                    raise ValueError(
                        "Identifier indicated by Flags but missing from payload"
                    )
                offset += 2

            # Combine remaining optional field checks into one branch to keep
            # static analysis branch count down.
            remaining_needed = offset
            if flags & 0x02:
                remaining_needed += 1
            if flags & 0x04:
                remaining_needed += 1
            if len(data) < remaining_needed:
                raise ValueError(
                    "Flags indicate additional fields are missing from payload"
                )
            # We don't need to advance offset further here because we only
            # validate presence (values are not returned in canonical output).

            return BatteryPowerStateData(
                raw_value=int(data[0]),
                battery_present=parsed["battery_present"],
                wired_external_power_connected=parsed["wired_external_power_connected"],
                wireless_external_power_connected=parsed[
                    "wireless_external_power_connected"
                ],
                battery_charge_state=parsed["battery_charge_state"],
                battery_charge_level=parsed["battery_charge_level"],
                battery_charging_type=parsed["battery_charging_type"],
                charging_fault_reason=parsed["charging_fault_reason"],
            )

        # Two-byte variant: first byte holds basic state, second byte encodes
        # charging type (bits 0-2) and fault bitmap (bits 3-7)
        charging_fault_reason: Any = None

        if len(data) >= 2:
            basic = self._parse_basic_state(state_raw)

            second = int(data[1])

            fault_raw = (second >> 3) & 0x1F
            if fault_raw != 0:
                fault_reasons: list[str] = []
                if fault_raw & 0x01:
                    fault_reasons.append("battery_fault")
                if fault_raw & 0x02:
                    fault_reasons.append("external_power_fault")
                if fault_raw & 0x04:
                    fault_reasons.append("other_fault")
                charging_fault_reason = (
                    fault_reasons[0] if len(fault_reasons) == 1 else fault_reasons
                )

            return BatteryPowerStateData(
                raw_value=state_raw,
                battery_present=basic["battery_present"],
                wired_external_power_connected=basic["wired_external_power_connected"],
                wireless_external_power_connected=basic[
                    "wireless_external_power_connected"
                ],
                battery_charge_state=basic["battery_charge_state"],
                battery_charge_level=basic["battery_charge_level"],
                battery_charging_type=BatteryChargingType.from_byte(second & 0x07),
                charging_fault_reason=charging_fault_reason,
            )

        # Single-byte basic variant
        basic = self._parse_basic_state(state_raw)
        return BatteryPowerStateData(
            raw_value=state_raw,
            battery_present=basic["battery_present"],
            wired_external_power_connected=basic["wired_external_power_connected"],
            wireless_external_power_connected=basic[
                "wireless_external_power_connected"
            ],
            battery_charge_state=basic["battery_charge_state"],
            battery_charge_level=basic["battery_charge_level"],
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
        encoded_byte = (
            battery_present_bits
            | (1 << 2 if data.wired_external_power_connected else 0)
            | (1 << 3 if data.wireless_external_power_connected else 0)
            | (charge_state_bits << 4)
            | (charge_level_bits << 6)
        )

        return bytearray([encoded_byte])

    def _parse_power_state_16(self, power_state_raw: int) -> dict[str, Any]:
        """Parse the 16-bit Power State bitfield into its components.

        Returns a dictionary with keys matching the public decode_value output.
        """
        # battery present (bit 0): 0 = No/Not present, 1 = Present
        battery_present = (
            BatteryPresentState.PRESENT
            if (power_state_raw & 0x01) == 1
            else BatteryPresentState.NOT_PRESENT
        )

        # Wired external power: bits 1-2 (2-bit value: 0=No,1=Yes,2=Unknown,3=RFU)
        wired_external_power_connected = ((power_state_raw >> 1) & 0x03) == 1

        # Wireless external power: bits 3-4
        wireless_external_power_connected = ((power_state_raw >> 3) & 0x03) == 1

        # Charge state: bits 5-6
        charge_state_raw = (power_state_raw >> 5) & 0x03
        battery_charge_state = BatteryChargeState.from_byte(charge_state_raw)

        # Charge level: bits 7-8
        charge_level_raw = (power_state_raw >> 7) & 0x03
        battery_charge_level = BatteryChargeLevel.from_byte(charge_level_raw)

        # charging type: bits 9-11
        charging_type_raw = (power_state_raw >> 9) & 0x07
        battery_charging_type = BatteryChargingType.from_byte(charging_type_raw)

        # charging faults are a 3-bit flag field at bits 12..14
        fault_bits = (power_state_raw >> 12) & 0x07
        fault_reasons: list[str] = []
        if fault_bits & 0x1:
            fault_reasons.append("battery_fault")
        if fault_bits & 0x2:
            fault_reasons.append("external_power_fault")
        if fault_bits & 0x4:
            fault_reasons.append("other_fault")

        charging_fault_reason = (
            fault_reasons[0] if len(fault_reasons) == 1 else fault_reasons or None
        )

        return {
            "battery_present": battery_present,
            "wired_external_power_connected": wired_external_power_connected,
            "wireless_external_power_connected": wireless_external_power_connected,
            "battery_charge_state": battery_charge_state,
            "battery_charge_level": battery_charge_level,
            "battery_charging_type": battery_charging_type,
            "charging_fault_reason": charging_fault_reason,
        }

    def _parse_basic_state(self, state_raw: int) -> dict[str, Any]:
        """Parse the single-byte basic state representation."""
        battery_present_raw = state_raw & 0x03
        battery_present = BatteryPresentState.from_byte(battery_present_raw)

        wired_external_power_connected = bool((state_raw >> 2) & 0x01)
        wireless_external_power_connected = bool((state_raw >> 3) & 0x01)

        charge_state_raw = (state_raw >> 4) & 0x03
        battery_charge_state = BatteryChargeState.from_byte(charge_state_raw)

        charge_level_raw = (state_raw >> 6) & 0x03
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

        return {
            "battery_present": battery_present,
            "wired_external_power_connected": wired_external_power_connected,
            "wireless_external_power_connected": wireless_external_power_connected,
            "battery_charge_state": battery_charge_state,
            "battery_charge_level": battery_charge_level,
        }

    @property
    def unit(self) -> str:
        """Unit for this characteristic (none)."""
        return ""
