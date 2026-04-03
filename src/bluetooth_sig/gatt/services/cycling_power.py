"""Cycling Power Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class CyclingPowerService(BaseGattService):
    """Cycling Power Service implementation (0x1818).

    Used for cycling power meters that measure power output in watts.
    Supports instantaneous power, force/torque vectors, and control
    functions.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.CYCLING_POWER_MEASUREMENT: True,
        CharacteristicName.CYCLING_POWER_FEATURE: True,
        CharacteristicName.CYCLING_POWER_VECTOR: False,
        CharacteristicName.CYCLING_POWER_CONTROL_POINT: False,
        CharacteristicName.SENSOR_LOCATION: True,
    }
