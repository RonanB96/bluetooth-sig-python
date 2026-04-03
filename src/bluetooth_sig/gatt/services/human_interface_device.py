"""Human Interface Device Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class HumanInterfaceDeviceService(BaseGattService):
    """Human Interface Device Service implementation.

    Contains characteristics related to HID:
    - HID Information - Required
    - HID Control Point - Required
    - Report Map - Required
    - Report - Conditional/Optional (device profile dependent)
    - Protocol Mode - Conditional/Optional (required for boot protocol support)
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.HID_INFORMATION: True,
        CharacteristicName.HID_CONTROL_POINT: True,
        CharacteristicName.REPORT_MAP: True,
        CharacteristicName.REPORT: False,
        CharacteristicName.PROTOCOL_MODE: False,
        CharacteristicName.BOOT_KEYBOARD_INPUT_REPORT: False,
        CharacteristicName.BOOT_KEYBOARD_OUTPUT_REPORT: False,
        CharacteristicName.BOOT_MOUSE_INPUT_REPORT: False,
    }
