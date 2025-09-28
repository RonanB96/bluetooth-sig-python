"""Heart Rate Service implementation."""

from dataclasses import dataclass
from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


@dataclass
class HeartRateService(BaseGattService):
    """Heart Rate Service implementation (0x180D).

    Used for heart rate monitoring devices. Contains the Heart Rate
    Measurement characteristic for heart rate data with optional RR-
    intervals and energy expenditure.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.HEART_RATE_MEASUREMENT: True,  # required
    }
