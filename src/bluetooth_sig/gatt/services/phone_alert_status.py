"""Phone Alert Status Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class PhoneAlertStatusService(BaseGattService):
    """Phone Alert Status Service implementation.

    Contains characteristics related to phone alert status:
    - Alert Status - Required
    - Ringer Setting - Required
    - Ringer Control Point - Optional
    """

    _service_name: str = "Phone Alert Status"

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.ALERT_STATUS: True,
        CharacteristicName.RINGER_SETTING: True,
        CharacteristicName.RINGER_CONTROL_POINT: False,
    }
