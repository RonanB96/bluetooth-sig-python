"""Boot Mouse Input Report characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class MouseButtons(IntFlag):
    """Mouse button states bitmap."""

    LEFT = 0x01
    RIGHT = 0x02
    MIDDLE = 0x04


class BootMouseInputReportData(msgspec.Struct, frozen=True, kw_only=True):
    """Boot mouse input report data.

    Attributes:
        buttons: Mouse button states bitmap
        x_displacement: Horizontal movement (signed, -127 to 127)
        y_displacement: Vertical movement (signed, -127 to 127)
        wheel: Optional scroll wheel movement (signed, -127 to 127)
    """

    buttons: MouseButtons
    x_displacement: int
    y_displacement: int
    wheel: int | None = None


class BootMouseInputReportCharacteristic(BaseCharacteristic):
    """Boot Mouse Input Report characteristic (0x2A33).

    org.bluetooth.characteristic.boot_mouse_input_report

    Contains mouse input report data in boot mode following USB HID boot protocol.
    Format: 3-4 bytes - buttons(1) + X(1) + Y(1) + [wheel(1)].

    Spec Reference:
        USB HID Specification v1.11, Appendix B - Boot Interface Descriptors
    """

    _manual_value_type = "BootMouseInputReportData"

    min_length = 3
    max_length = 4
    allow_variable_length = True

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> BootMouseInputReportData:
        """Parse HID mouse report.

        Args:
            data: Raw bytearray from BLE characteristic (3-4 bytes).
            ctx: Optional CharacteristicContext.

        Returns:
            BootMouseInputReportData with parsed mouse state.
        """
        buttons = MouseButtons(data[0])
        x_displacement = DataParser.parse_int8(data, 1, signed=True)
        y_displacement = DataParser.parse_int8(data, 2, signed=True)
        wheel = DataParser.parse_int8(data, 3, signed=True) if len(data) == 4 else None

        return BootMouseInputReportData(
            buttons=buttons,
            x_displacement=x_displacement,
            y_displacement=y_displacement,
            wheel=wheel,
        )

    def encode_value(self, data: BootMouseInputReportData) -> bytearray:
        """Encode mouse report to bytes.

        Args:
            data: BootMouseInputReportData to encode

        Returns:
            Encoded bytes (3-4 bytes depending on wheel presence)
        """
        result = bytearray()
        result.append(int(data.buttons))
        result.extend(DataParser.encode_int8(data.x_displacement, signed=True))
        result.extend(DataParser.encode_int8(data.y_displacement, signed=True))

        if data.wheel is not None:
            result.extend(DataParser.encode_int8(data.wheel, signed=True))

        return result
