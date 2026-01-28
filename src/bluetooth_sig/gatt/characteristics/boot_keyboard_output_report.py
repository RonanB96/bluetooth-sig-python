"""Boot Keyboard Output Report characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class KeyboardLEDs(IntFlag):
    """Keyboard LED states bitmap."""

    NUM_LOCK = 0x01
    CAPS_LOCK = 0x02
    SCROLL_LOCK = 0x04
    COMPOSE = 0x08
    KANA = 0x10


class BootKeyboardOutputReportCharacteristic(BaseCharacteristic[KeyboardLEDs]):
    """Boot Keyboard Output Report characteristic (0x2A32).

    org.bluetooth.characteristic.boot_keyboard_output_report

    Contains keyboard LED states from host to keyboard following USB HID boot protocol.
    Format: 1 byte - LED states bitmap.

    Spec Reference:
        USB HID Specification v1.11, Appendix B - Boot Interface Descriptors
    """

    _manual_value_type = "KeyboardLEDs"

    min_length = 1
    max_length = 1
    allow_variable_length = False

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> KeyboardLEDs:
        """Parse keyboard LED states.

        Args:
            data: Raw bytearray from BLE characteristic (1 byte).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True)

        Returns:
            KeyboardLEDs with parsed LED states.
        """
        return KeyboardLEDs(data[0])

    def _encode_value(self, data: KeyboardLEDs) -> bytearray:
        """Encode LED states to bytes.

        Args:
            data: KeyboardLEDs to encode

        validate: Whether to validate ranges (default True)

        Returns:
            Encoded bytes (1 byte)
        """
        return bytearray([int(data)])
