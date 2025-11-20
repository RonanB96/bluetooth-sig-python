"""Immediate Alert Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class ImmediateAlertService(BaseGattService):
    """Immediate Alert Service implementation.

    Exposes a control point to allow a peer device to cause the device to
    immediately alert.

    Contains characteristics related to immediate alerts:
    - Alert Level - Required
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.ALERT_LEVEL: True,  # required
    }
