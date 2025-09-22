"""Cycling Speed and Cadence Service implementation."""

from dataclasses import dataclass
from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


@dataclass
class CyclingSpeedAndCadenceService(BaseGattService):
    """Cycling Speed and Cadence Service implementation (0x1816).

    Used for cycling sensors that measure wheel and crank revolutions.
    Contains the CSC Measurement characteristic for cycling metrics.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.CSC_MEASUREMENT: True,  # required
    }
