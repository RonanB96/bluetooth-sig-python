"""Battery-related enumerations for power state characteristics.

Defines enums for battery charge states, charge levels, charging types,
and fault reasons to replace string usage with type-safe alternatives.
"""

from __future__ import annotations

from enum import IntEnum


class PowerConnectionState(IntEnum):
    """Power connection state enumeration."""

    NO = 0
    YES = 1
    UNKNOWN = 2
    RFU = 3


class BatteryChargeState(IntEnum):
    """Battery charge state enumeration."""

    UNKNOWN = 0
    CHARGING = 1
    DISCHARGING = 2
    NOT_CHARGING = 3

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

    @classmethod
    def from_byte(cls, byte_val: int) -> BatteryChargingType:
        """Create enum from byte value with fallback."""
        try:
            return cls(byte_val)
        except ValueError:
            return cls.UNKNOWN


class ServiceRequiredState(IntEnum):
    """Service required state enumeration."""

    FALSE = 0
    TRUE = 1
    UNKNOWN = 2
    RFU = 3


class BatteryFaultReason(IntEnum):
    """Battery fault reason enumeration."""

    BATTERY_FAULT = 0
    EXTERNAL_POWER_FAULT = 1
    OTHER_FAULT = 2
