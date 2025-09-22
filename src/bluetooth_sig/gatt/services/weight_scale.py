"""Weight Scale Service implementation."""

from dataclasses import dataclass
from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


@dataclass
class WeightScaleService(BaseGattService):
    """Weight Scale Service implementation (0x181D).

    Used for smart scale devices that measure weight and related body metrics.
    Contains Weight Measurement and Weight Scale Feature characteristics.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.WEIGHT_MEASUREMENT: True,  # required
        CharacteristicName.WEIGHT_SCALE_FEATURE: False,  # optional
    }
