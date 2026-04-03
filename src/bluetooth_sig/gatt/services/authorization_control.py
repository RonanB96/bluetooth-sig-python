"""AuthorizationControl Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class AuthorizationControlService(BaseGattService):
    """Authorization Control Service implementation (0x183D).

    Provides authorisation control for BLE service access using
    a challenge-response mechanism.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.ACS_CONTROL_POINT: True,
        CharacteristicName.ACS_DATA_IN: False,
        CharacteristicName.ACS_DATA_OUT_INDICATE: False,
        CharacteristicName.ACS_DATA_OUT_NOTIFY: False,
        CharacteristicName.ACS_STATUS: True,
    }
