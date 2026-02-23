"""Boot Keyboard Input Report characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..constants import SIZE_UINT16
from ..context import CharacteristicContext
from .base import BaseCharacteristic


class KeyboardModifiers(IntFlag):
    """Keyboard modifier keys bitmap."""

    LEFT_CTRL = 0x01
    LEFT_SHIFT = 0x02
    LEFT_ALT = 0x04
    LEFT_GUI = 0x08
    RIGHT_CTRL = 0x10
    RIGHT_SHIFT = 0x20
    RIGHT_ALT = 0x40
    RIGHT_GUI = 0x80


class BootKeyboardInputReportData(msgspec.Struct, frozen=True, kw_only=True):
    """Boot keyboard input report data.

    Attributes:
        modifiers: Modifier keys state bitmap
        reserved: Reserved byte (always 0)
        keycodes: Up to 6 simultaneous key codes (HID usage IDs)
    """

    modifiers: KeyboardModifiers
    reserved: int
    keycodes: tuple[int, ...]


class BootKeyboardInputReportCharacteristic(BaseCharacteristic[BootKeyboardInputReportData]):
    """Boot Keyboard Input Report characteristic (0x2A22).

    org.bluetooth.characteristic.boot_keyboard_input_report

    Contains keyboard input report data in boot mode following USB HID boot protocol.
    Format: 1-8 bytes - modifier(1) + [reserved(1) + keycodes(0-6)].

    Spec Reference:
        USB HID Specification v1.11, Appendix B - Boot Interface Descriptors
    """

    min_length = 1
    max_length = 8
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> BootKeyboardInputReportData:
        """Parse HID keyboard report.

        Args:
            data: Raw bytearray from BLE characteristic (1-8 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True)

        Returns:
            BootKeyboardInputReportData with parsed keyboard state.
        """
        modifiers = KeyboardModifiers(data[0])
        reserved = data[1] if len(data) >= SIZE_UINT16 else 0
        keycodes = tuple(data[i] for i in range(2, len(data)))

        return BootKeyboardInputReportData(
            modifiers=modifiers,
            reserved=reserved,
            keycodes=keycodes,
        )

    def _encode_value(self, data: BootKeyboardInputReportData) -> bytearray:
        """Encode keyboard report to bytes.

        Args:
            data: BootKeyboardInputReportData to encode

        validate: Whether to validate ranges (default True)

        Returns:
            Encoded bytes (8 bytes total)
        """
        result = bytearray(8)
        result[0] = int(data.modifiers)
        result[1] = data.reserved

        # Encode up to 6 keycodes
        for i, keycode in enumerate(data.keycodes[:6]):
            result[2 + i] = keycode

        return result
