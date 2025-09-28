"""Running Speed and Cadence Service implementation."""

from dataclasses import dataclass
from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


@dataclass
class RunningSpeedAndCadenceService(BaseGattService):
    """Running Speed and Cadence Service implementation (0x1814).

    Used for running sensors that measure speed, cadence, stride length,
    and distance. Contains the RSC Measurement characteristic for
    running metrics.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.RSC_MEASUREMENT: True,  # required
    }
