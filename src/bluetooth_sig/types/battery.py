"""Battery-related enumerations for power state characteristics.

Defines enums for battery charge states, charge levels, charging types,
and fault reasons to replace string usage with type-safe alternatives.
"""

from __future__ import annotations

from enum import Enum


class BatteryChargeState(Enum):
    """Battery charge state enumeration."""

    UNKNOWN = "unknown"
    CHARGING = "charging"
    DISCHARGING = "discharging"
    NOT_CHARGING = "not_charging"

    @classmethod
    def from_byte(cls, byte_val: int) -> BatteryChargeState:
        """Create enum from byte value with fallback."""
        mapping = {
            0: cls.UNKNOWN,
            1: cls.CHARGING,
            2: cls.DISCHARGING,
            3: cls.NOT_CHARGING,
        }
        return mapping.get(byte_val, cls.UNKNOWN)


class BatteryChargeLevel(Enum):
    """Battery charge level enumeration."""

    UNKNOWN = "unknown"
    GOOD = "good"
    LOW = "low"
    CRITICALLY_LOW = "critically_low"

    @classmethod
    def from_byte(cls, byte_val: int) -> BatteryChargeLevel:
        """Create enum from byte value with fallback."""
        mapping = {
            0: cls.UNKNOWN,
            1: cls.GOOD,
            2: cls.LOW,
            3: cls.CRITICALLY_LOW,
        }
        return mapping.get(byte_val, cls.UNKNOWN)


class BatteryChargingType(Enum):
    """Battery charging type enumeration."""

    UNKNOWN = "unknown"
    CONSTANT_CURRENT = "constant_current"
    CONSTANT_VOLTAGE = "constant_voltage"
    TRICKLE = "trickle"
    FLOAT = "float"
    CONSTANT_POWER = "constant_power"

    @classmethod
    def from_byte(cls, byte_val: int) -> BatteryChargingType:
        """Create enum from byte value with fallback."""
        mapping = {
            0: cls.UNKNOWN,
            1: cls.CONSTANT_CURRENT,
            2: cls.CONSTANT_VOLTAGE,
            3: cls.TRICKLE,
            4: cls.FLOAT,
            5: cls.CONSTANT_POWER,
        }
        return mapping.get(byte_val, cls.UNKNOWN)


class BatteryFaultReason(Enum):
    """Battery fault reason enumeration."""

    BATTERY_FAULT = "battery_fault"
    EXTERNAL_POWER_FAULT = "external_power_fault"
    OTHER_FAULT = "other_fault"
