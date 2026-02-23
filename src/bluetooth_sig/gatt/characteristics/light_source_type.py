"""Light Source Type characteristic (0x2BE4)."""

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
    """

    NOT_SPECIFIED = 0x00
    LOW_PRESSURE_FLUORESCENT = 0x01
    HID = 0x02
    LOW_VOLTAGE_HALOGEN = 0x03
    INCANDESCENT = 0x04
    LED = 0x05


class LightSourceTypeCharacteristic(BaseCharacteristic[LightSourceTypeValue]):
    """Light Source Type characteristic (0x2BE4).

    org.bluetooth.characteristic.light_source_type

    Type of light source (LED, fluorescent, incandescent, etc.).
    """

    _template = EnumTemplate.uint8(LightSourceTypeValue)
