"""Light Source Type characteristic (0x2BE3)."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class LightSourceTypeValue(IntEnum):
    """Light source type values.

    Values:
        NOT_SPECIFIED: Type not specified (0x00)
        LOW_PRESSURE_FLUORESCENT: Low pressure fluorescent (0x01)
        HID: High intensity discharge (0x02)
        LOW_VOLTAGE_HALOGEN: Low voltage halogen (0x03)
        INCANDESCENT: Incandescent (0x04)
        LED: Light emitting diode (0x05)
        OLED: Organic light emitting diode (0x06)
        OTHER: Other than listed above (0xFD)
        NO_LIGHT_SOURCE: No light source (0xFE)
        MULTIPLE: Multiple light source types (0xFF)
    """

    NOT_SPECIFIED = 0x00
    LOW_PRESSURE_FLUORESCENT = 0x01
    HID = 0x02
    LOW_VOLTAGE_HALOGEN = 0x03
    INCANDESCENT = 0x04
    LED = 0x05
    OLED = 0x06
    OTHER = 0xFD
    NO_LIGHT_SOURCE = 0xFE
    MULTIPLE = 0xFF


class LightSourceTypeCharacteristic(BaseCharacteristic[LightSourceTypeValue]):
    """Light Source Type characteristic (0x2BE3).

    org.bluetooth.characteristic.light_source_type

    Type of light source (LED, fluorescent, incandescent, etc.).
    """

    _template = EnumTemplate.uint8(LightSourceTypeValue)
