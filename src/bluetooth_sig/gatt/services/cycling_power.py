"""Cycling Power Service implementation."""

from dataclasses import dataclass
from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


@dataclass
class CyclingPowerService(BaseGattService):
    """Cycling Power Service implementation (0x1818).

    Used for cycling power meters that measure power output in watts.
    Supports instantaneous power, force/torque vectors, and control
    functions.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.CYCLING_POWER_MEASUREMENT: True,  # required
        CharacteristicName.CYCLING_POWER_FEATURE: True,  # required
        CharacteristicName.CYCLING_POWER_VECTOR: False,  # optional
        CharacteristicName.CYCLING_POWER_CONTROL_POINT: False,  # optional
    }
