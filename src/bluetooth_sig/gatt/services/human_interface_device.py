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
    - Report - Required
    - Protocol Mode - Required
    - PnP ID - Optional
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.HID_INFORMATION: True,  # required
        CharacteristicName.HID_CONTROL_POINT: True,  # required
        CharacteristicName.REPORT_MAP: True,  # required
        CharacteristicName.REPORT: True,  # required
        CharacteristicName.PROTOCOL_MODE: True,  # required
        # CharacteristicName.PNP_ID: False,  # optional - not implemented yet
    }
