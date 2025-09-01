"""Battery Power State characteristic implementation."""

from dataclasses import dataclass
from typing import Any, Dict

from .base import BaseCharacteristic


@dataclass
class BatteryPowerStateCharacteristic(BaseCharacteristic):
    """Battery Power State characteristic (0x2A1A).

    Provides comprehensive battery status information beyond just the level percentage,
    including power sources, charge state, charge level, charging type, and fault information.
    """

    _characteristic_name: str = "Battery Power State"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "string"  # Complex data structure
        super().__post_init__()

    def parse_value(self, data: bytearray) -> Dict[str, Any]:
        """Parse battery power state data according to expected bit field format.

        Format: Battery Power State(1 byte) - bitmask indicating various battery states

        Bit field interpretation:
        - Bit 0-1: Battery Present State
          00 = Unknown
          01 = Battery not present
          10 = Battery present
          11 = Reserved
        - Bit 2: Wired External Power Source Connected (0 = No, 1 = Yes)
        - Bit 3: Wireless External Power Source Connected (0 = No, 1 = Yes)
        - Bit 4-5: Battery Charge State
          00 = Unknown
          01 = Charging
          10 = Discharging
          11 = Not charging
        - Bit 6-7: Battery Charge Level
          00 = Unknown
          01 = Critically low
          10 = Low
          11 = Good

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Dict containing parsed battery power state information

        Raises:
            ValueError: If data format is invalid
        """
        if not data:
            raise ValueError("Battery Power State data must be at least 1 byte")

        state_raw = data[0]

        # Parse basic battery state information
        basic_state = self._parse_basic_state(state_raw)

        # Parse extended information if available
        extended_info = self._parse_extended_info(data)

        # Combine basic and extended information
        result = {**basic_state, **extended_info}
        result["raw_value"] = state_raw

        return result

    def _parse_basic_state(self, state_raw: int) -> Dict[str, Any]:
        """Parse basic battery state from the first byte.

        Args:
            state_raw: Raw state byte value

        Returns:
            Dict containing basic battery state information
        """
        # Parse battery present state (bits 0-1)
        battery_present_raw = state_raw & 0x03
        battery_present_map = {
            0: "unknown",
            1: "not_present",
            2: "present",
            3: "reserved",
        }

        # Parse power sources (bits 2-3)
        wired_power = bool(state_raw & 0x04)
        wireless_power = bool(state_raw & 0x08)

        # Parse charge state (bits 4-5)
        charge_state_raw = (state_raw >> 4) & 0x03
        charge_state_map = {
            0: "unknown",
            1: "charging",
            2: "discharging",
            3: "not_charging",
        }

        # Parse charge level (bits 6-7)
        charge_level_raw = (state_raw >> 6) & 0x03
        charge_level_map = {
            0: "unknown",
            1: "critically_low",
            2: "low",
            3: "good",
        }

        return {
            "battery_present": battery_present_map.get(battery_present_raw, "unknown"),
            "wired_external_power_connected": wired_power,
            "wireless_external_power_connected": wireless_power,
            "battery_charge_state": charge_state_map.get(charge_state_raw, "unknown"),
            "battery_charge_level": charge_level_map.get(charge_level_raw, "unknown"),
        }

    def _parse_extended_info(self, data: bytearray) -> Dict[str, Any]:
        """Parse extended battery information from additional bytes.

        Args:
            data: Complete raw bytearray from BLE characteristic

        Returns:
            Dict containing extended battery information
        """
        charging_type = "unknown"
        charging_fault_reason = None

        if len(data) >= 2:
            # Parse charging type from second byte (bits 0-2)
            charging_type_raw = data[1] & 0x07
            charging_type_map = {
                0: "unknown",
                1: "constant_current",
                2: "constant_voltage",
                3: "trickle",
                4: "constant_power",
                5: "reserved_5",
                6: "reserved_6",
                7: "reserved_7",
            }
            charging_type = charging_type_map.get(charging_type_raw, "unknown")

            # Parse charging fault reason (bits 3-7)
            fault_raw = (data[1] >> 3) & 0x1F
            if fault_raw != 0:
                fault_map = {
                    1: "battery_fault",
                    2: "external_power_fault",
                    3: "other_fault",
                    4: "unknown_fault",
                    5: "reserved_fault_5",
                    # Add more fault codes as needed
                }
                charging_fault_reason = fault_map.get(
                    fault_raw, f"fault_code_{fault_raw}"
                )

        return {
            "battery_charging_type": charging_type,
            "charging_fault_reason": charging_fault_reason,
        }

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""  # No unit for status information

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "battery"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return ""  # Status characteristics don't have measurement state class
